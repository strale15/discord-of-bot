from email import message
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict

import settings
from util import *
from classes import publish_hw_sheet_ppv as ppvSheet
from classes import publish_hw_sheet_mm as mmSheet
from classes.publish_hw_sheet_ppv import PPVHomeworkSubmission
from classes.publish_hw_sheet_mm import MMHomeworkSubmission
import util

class PublishHwCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(date="Date in YYYY-MM-DD format")
    @app_commands.command(name="hw-publish", description="Sends a DM with grades to all trainees who completed the homework for given date")
    async def publishHw(self, interaction: discord.Interaction, date: str):
        await interaction.response.defer(ephemeral=True)
        
        trainer_role = interaction.guild.get_role(settings.TRAINER_ROLE_ID)
        if trainer_role not in interaction.user.roles:
            await interaction.followup.send("You do not have a _Trainer_ role.")
            return
        
        if not self.is_valid_date(date):
            await interaction.followup.send("Invalid date format. Use `YYYY-MM-DD` (e.g., `2025-06-11`).")
            return
        
        ppv_rows = ppvSheet.fetch_rows_by_date(date)
        isPpvPresentForDate = True
        if not ppv_rows or len(ppv_rows) == 0:
            isPpvPresentForDate = False
            #await interaction.followup.send(f"No ppv hw data found for date `{date}`.")
        else:
            ppv_trainee_messages = self.build_ppv_messages_by_trainee(ppv_rows, date)
            
        mma_rows = mmSheet.fetch_rows_by_date(date)
        isMmaPresentForDate = True
        if not mma_rows or len(mma_rows) == 0:
            isMmaPresentForDate = False
        else:
            mma_trainee_messages = self.build_mma_messages_by_trainee(mma_rows, date)

        all_trainee_ids = set()
        if isPpvPresentForDate:
            all_trainee_ids.update(ppv_trainee_messages.keys())
        if isMmaPresentForDate:
            all_trainee_ids.update(mma_trainee_messages.keys())

        for trainee_id in all_trainee_ids:
            full_msg = f"## 📝 Here are your homework results for `{date}`:\n\n"

            if isPpvPresentForDate and trainee_id in ppv_trainee_messages:
                full_msg += ppv_trainee_messages[trainee_id] + "\n\n"

            if isMmaPresentForDate and trainee_id in mma_trainee_messages:
                full_msg += mma_trainee_messages[trainee_id] + "\n\n"

            try:
                member = await interaction.guild.fetch_member(int(trainee_id))
                await util.send_dm(member, full_msg)
            except Exception as e:
                continue
            
        msg = "Homework published!"
        
        if not isPpvPresentForDate:
            msg += " No PPV data for provided date."
        if not isMmaPresentForDate:
            msg += " No MM data for provided date."
            
        await interaction.followup.send(msg)
        
    def build_ppv_messages_by_trainee(self, ppv_rows, date: str) -> dict[str, str]:
        messages = defaultdict(str)

        grouped_rows = self.group_ppv_rows_by_trainee(ppv_rows)

        for trainee_id, trainee_rows in grouped_rows.items():
            member_msg = ""

            for submission in trainee_rows:
                notes = submission.notes.strip() if submission.notes.strip() else "/"
                response = submission.response.strip() if submission.response.strip() else "/"

                result_block = (
                    f"**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                    f"- Grade: `{submission.grade}` | "
                    f"Self rate: `{submission.self_rate}` | "
                    f"Completion time: `{submission.completion_time}`\n\n"
                    f"Notes:\n```{notes}```\n"
                    f"Submission:\n```{response}```\n"
                )

                member_msg += result_block
            
            messages[trainee_id] = member_msg

        return messages
    
    def build_mma_messages_by_trainee(self, mma_rows, date: str) -> dict[str, str]:
        messages = defaultdict(str)

        grouped_rows = self.group_mma_rows_by_trainee(mma_rows)

        for trainee_id, trainee_rows in grouped_rows.items():
            member_msg = ""
            
            for submission in trainee_rows:
                notes = submission.notes.strip() if submission.notes.strip() else "/"

                result_block = (
                    f"**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                    f"- Grade: `{submission.grade}`\n"
                    f"Notes:\n```{notes}```\n"
                    f"MM1:\n```{submission.mm1}```\n"
                    f"MM2:\n```{submission.mm2}```\n"
                    f"MM3:\n```{submission.mm3}```\n"
                    f"MM4:\n```{submission.mm4}```\n"
                    f"MM5:\n```{submission.mm5}```\n"
                )

                member_msg += result_block
            
            messages[trainee_id] = member_msg

        return messages
    
    def group_ppv_rows_by_trainee(self, rows: List[PPVHomeworkSubmission]) -> Dict[str, List[PPVHomeworkSubmission]]:
        grouped = defaultdict(list)
        for row in rows:
            grouped[row.trainee_id].append(row)
        return grouped
    
    def group_mma_rows_by_trainee(self, rows: List[MMHomeworkSubmission]) -> Dict[str, List[MMHomeworkSubmission]]:
        grouped = defaultdict(list)
        for row in rows:
            grouped[row.trainee_id].append(row)
        return grouped
    
    def is_valid_date(self, date_str: str) -> bool:
        # Strict YYYY-MM-DD format with leading zero enforcement
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
        
    async def cog_load(self):
        self.bot.tree.add_command(self.publishHw, guild=settings.TRAIN_GUILD_ID)

async def setup(bot):
    await bot.add_cog(PublishHwCog(bot))
    

    

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
from classes import publish_hw_sheet_ppv as publishSheet
from classes.publish_hw_sheet_ppv import HomeworkSubmission
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
        
        if not is_valid_date(date):
            await interaction.followup.send("Invalid date format. Use `YYYY-MM-DD` (e.g., `2025-06-11`).")
            return
        
        rows = publishSheet.fetch_rows_by_date(date)
        if not rows or len(rows) == 0:
            await interaction.followup.send(f"No hw data found for date `{date}`.")
            return

        grouped_rows = group_rows_by_trainee(rows)

        for trainee_id, trainee_rows in grouped_rows.items():
            try:
                member = await interaction.guild.fetch_member(int(trainee_id))
            except:
                continue
            
            member_msg = f"## 📝 Here are your homework results for `{date}`:\n\n"
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
            
            await util.send_dm(member, member_msg)

        await interaction.followup.send("Homework published!")
        
    async def cog_load(self):
        self.bot.tree.add_command(self.publishHw, guild=settings.TRAIN_GUILD_ID)

async def setup(bot):
    await bot.add_cog(PublishHwCog(bot))
    
def is_valid_date(date_str: str) -> bool:
    # Strict YYYY-MM-DD format with leading zero enforcement
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def group_rows_by_trainee(rows: List[HomeworkSubmission]) -> Dict[str, List[HomeworkSubmission]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.trainee_id].append(row)
    return grouped
import discord
from discord.ext import commands
from discord import app_commands, Interaction
import re

import settings
import util
from classes import mm_train_db as mmdb
from classes import mmSheet as mmsheet
from util import *

class MMTrainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not isinstance(message.channel, discord.DMChannel):
            return
        
        lines = message.content.splitlines()
        first_line = lines[0].lower()
        
        match = re.match(r"^submit mm ([0-9]+)\s*$", first_line)
        if match:
            hw_id = match.group(1)
            trainee_id = message.author.id
            
            if len(lines) < 2:
                await message.channel.send(f"You are trying to submit an empty mm for homework code **{hw_id}**.")
                return
            
            if not mmdb.is_mm_hw_assigned_and_not_completed(hw_id, trainee_id):
                await message.channel.send(f"Homework id **{hw_id}** is not assigned to you.")
                return
            
            mm_msg = "\n".join(lines[1:]).strip()
            mms, schedule_date = mmdb.submit_next_mm(hw_id, trainee_id, mm_msg)
            
            if mms is None:
                await message.channel.send(f"You have already completed homework id **{hw_id}**.")
                return
            
            mms_left = 5 - len(mms)
            
            if mms_left == 0:
                msg = await message.channel.send("*Processing, please wait...*")

                discord_display_name = await util.get_train_guild_display_name_from_user_id(self.bot, trainee_id)
                date = schedule_date.strftime("%Y-%m-%d %H:%M")
                mmsheet.submit_hw_to_sheet(date, discord_display_name, mms)
                
                await msg.edit(content=f"Thanks for submitting final mm for homework id **{hw_id}**, nice work!")
            else:
                await message.channel.send(f"Thanks for submitting mm for homework id **{hw_id}**, {mms_left} *more mms left.*")
            return
        
    @app_commands.command(name="hw-mm", description="Gives homework to trainees that are in the same voice call as you")
    async def giveMmHomework(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        trainer_role = interaction.guild.get_role(settings.TRAINER_ROLE_ID)
        if trainer_role not in interaction.user.roles:
            await interaction.followup.send("You do not have a _Trainer_ role.")
            return
        
        trainees = await util.extract_trainees_from_voice(interaction)
        
        if trainees is not None and len(trainees) > 0:
            for trainee in trainees:
                await self.generate_mm_hw_for_trainee(trainee)
            
        message = await interaction.followup.send("Successfully generated MM homework for all trainees.")
        asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
        
    async def generate_mm_hw_for_trainee(self, trainee: discord.Member):
        hw_id = mmdb.insert_mm_train(trainee.id)
        msg = f"""Mass message homework with the following code was generated for you: **{hw_id}**
Please submit **5** mass messages **one by one** by sending me a message in the following format:

submit mm {hw_id}

*your mm*

fu1
*your fu1*

fu2
*your fu2*
-# ...and so on"""
        await util.send_dm(trainee, msg)
        
    async def cog_load(self):
        self.bot.tree.add_command(self.giveMmHomework, guild=settings.TRAIN_GUILD_ID)
        pass

async def setup(bot):
    await bot.add_cog(MMTrainCog(bot))
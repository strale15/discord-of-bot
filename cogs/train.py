import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random
import re

import settings
from util import *
import util
from classes import trainingdb as db
from classes import ppvSheet as ppvsheet

class TrainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.started_example = []
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not isinstance(message.channel, discord.DMChannel):
            return
            
        #START hw
        match = re.match(r"^start\s+(ctx_[0-9]{3})$", message.content.lower())
        if match:
            img_id = match.group(1)
            trainee_id = message.author.id
            
            if not db.is_hw_startable(img_id, trainee_id):
                await message.channel.send(f"This code was either not assigned to you/you have already completed it/you already started it.")
                return
            
            ppv_hw_instruction = f"""Write a PPV for this scenario (**{img_id}**), in format:
end [code]

PPV caption

PPV followup
"""
            db.start_hw(img_id, trainee_id)
            
            file_id = util.getCtxImgDriveId(img_id=img_id)
            embed = discord.Embed(title="PPV scenario image:", description="*(if empty please wait for it to load...)*")
            embed.set_image(url=f"https://drive.google.com/uc?export=view&id={file_id}")
            await message.channel.send(ppv_hw_instruction, embed=embed)
            return
            
        #END hw
        first_line = message.content.splitlines()[0].lower()
        match = re.match(r"^end\s+(ctx_[0-9]{3})$", first_line)
        if match:
            img_id = match.group(1)
            trainee_id = message.author.id
            
            lines = message.content.splitlines()
            if len(lines) < 2:
                await message.channel.send(f"You are trying to submit an empty response for homework code {img_id}.")
                return
            
            response = "\n".join(lines[1:]).strip()
            
            if not db.is_hw_in_progress(img_id, trainee_id):
                await message.channel.send(f"You either completed this homework or have not started it yet. Send me 'start [code]' if you want to start it.")
                return
            
            #Submit hw
            msg = await message.channel.send(f"_Submitting, please wait..._")
            start_time, img_id, trainee_id, completion_time, response = db.end_hw(img_id, trainee_id, response)
            
            completion_time_minutes = int(completion_time // 60)
            completion_time_seconds = round(completion_time % 60)
            completion_time_str = f"{completion_time_minutes}m {completion_time_seconds}s"
            
            discord_display_name = await util.get_train_guild_display_name_from_user_id(self.bot, trainee_id)
            date = start_time.strftime("%Y-%m-%d %H:%M")
            
            ppvsheet.submit_hw_to_sheet(date, img_id, discord_display_name, completion_time_str, response)
            
            await msg.edit(content=f"Thanks for submitting the homework code **{img_id}**. Your response was recorded.")
            return
        
        #Start HW example
        if message.content.lower() == "start ctx_example":     
            ppv_hw_instruction = f"""Write a PPV for this scenario (**ctx_example**), in format:
end [code] <- You will wirte an actual homework code like ctx_001 or in this case ctx_example

PPV caption <- Here you write PPV caption

PPV followup <- Here you write the PPV followup
"""
            await message.channel.send(ppv_hw_instruction, file=discord.File(f"resources/training/context_example/ctx_example.png"))
            
            ppv_hw_instruction = f"""*For this example you would submit your response like:*
end ctx_example

some ppv caption

some ppv followup
"""
            await message.channel.send(ppv_hw_instruction)
            return
            
        #End HW example
        first_line = message.content.splitlines()[0].lower()
        if first_line == "end ctx_example":
            lines = message.content.splitlines()
            
            if len(lines) < 2:
                await message.channel.send(f"You successfully ended hw example but your ppv caption and followup are probably missing.")
                return
            
            await message.channel.send(f"Thanks for submitting the homework code **ctx_example**. Your successfully completed ppv example.")
            return
        
    @app_commands.command(name="hw", description="Gives homework to trainees that are in the same voice call as you")
    async def giveHomework(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        trainer_role = interaction.guild.get_role(settings.TRAINER_ROLE_ID)
        if trainer_role not in interaction.user.roles:
            await interaction.followup.send("You do not have a _Trainer_ role.")
            return
        
        trainees = await self.extract_trainees_from_voice(interaction)
        
        if trainees is not None and len(trainees) > 0:
            for trainee in trainees:
                await self.generate_hw_for_trainee(interaction, trainee)
            
        await interaction.followup.send("Successfully generated homework for all trainees.")
        
    async def extract_trainees_from_voice(self, interaction: discord.Interaction) -> list[discord.Member]:
        user_voice = interaction.user.voice

        if not user_voice or not user_voice.channel:
            await interaction.followup.send("You're not in a voice channel.")
            return

        voice_channel = user_voice.channel
        
        trainee_role = interaction.guild.get_role(settings.TRAINEE_ROLE_ID)
        chatter_role = interaction.guild.get_role(settings.CHATTER_ROLE_ID)
        
        trainees = [
            member for member in voice_channel.members
            if trainee_role in member.roles and chatter_role not in member.roles
        ]
        
        if len(trainees) == 0:
            await interaction.followup.send("No trainees in your voice channel.")
            return
        
        return trainees
    
    async def generate_hw_for_trainee(self, interaction: discord.Interaction, trainee: discord.Member):
        img_codes = []
        existing_img_ids = db.get_img_ids_for_trainee(trainee.id)
        
        for i in range(3):
            img_id = self.generate_random_img_id(existing_img_ids)
            
            if img_id is None:
                break
                
            img_codes.append(img_id)
            db.insert_hw_schedule(img_id=img_id, trainee_id=trainee.id)
        
        if len(img_codes) == 0:
            await self.send_dm(trainee, "Congrats, you have completed all available ppv homeworks for now!")
            return
            
        codes_str = ", ".join(img_codes)
        hw_msg = f"""Homework with the following codes was generated for you: **{codes_str}**.
When you are ready to start an exercises send 'start [code]' for example 'start {img_codes[0]}'.

_Note:_ These responses are timed!

*If this is your first time doing the homework or you forgot how to do it you can go trough an example just send 'start ctx_example'.*
"""
        await self.send_dm(trainee, hw_msg)
            
    def generate_random_img_id(self, existing_img_ids):
        num_of_ctx_imgs = util.countContextImages()
        if len(existing_img_ids) >= num_of_ctx_imgs:
            return None
        
        while True:
            num = random.randint(1, num_of_ctx_imgs)
            img_id = f"ctx_{num:03}"
            if img_id not in existing_img_ids:
                return img_id
            
    async def send_dm(self, memeber: discord.Member, msg):
        try:
            await memeber.send(msg)
        except discord.Forbidden:
            log.info(f"Could not send a join DM to {memeber.name}")
        
    async def cog_load(self):
        self.bot.tree.add_command(self.giveHomework, guild=settings.TRAIN_GUILD_ID)

async def setup(bot):
    await bot.add_cog(TrainCog(bot))
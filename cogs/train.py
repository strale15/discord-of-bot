import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random

import settings
from util import *
import util
from classes import trainingdb as db

class TrainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
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
        existing_img_ids = db.get_img_ids_for_trainee(trainee.id)
        img_id = self.generate_random_img_id(existing_img_ids)
        
        if img_id is None:
            await self.send_dm(trainee, "Congrats, you have completed all available homeworks for now!")
            return
        
        try:
            db.insert_hw_schedule(img_id=img_id, trainee_id=trainee.id)
            await self.send_dm(trainee, f"Homework with id: {img_id} was generated for you.")
        except:
            log.warning(f"Error generating homework for {trainee.display_name}")
            
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
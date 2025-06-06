import discord
from discord.ext import commands
from discord import app_commands, Interaction

import settings
from util import *

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
    
    async def generate_hw_for_trainee(self, interaction: discord.Interaction, trinee: discord.Member):
        try:
            await trinee.send("Hi. This is a test hw msg.")
        except discord.Forbidden:
            log.info(f"Could not send a join DM to {trinee.name}")
        
    async def cog_load(self):
        self.bot.tree.add_command(self.giveHomework, guild=settings.TRAIN_GUILD_ID)

async def setup(bot):
    await bot.add_cog(TrainCog(bot))
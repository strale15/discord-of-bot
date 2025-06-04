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
        user_voice = interaction.user.voice

        if not user_voice or not user_voice.channel:
            await interaction.response.send_message("You're not in a voice channel.", ephemeral=True)
            return

        voice_channel = user_voice.channel
        members = voice_channel.members
        member_names = [member.display_name for member in members]

        await interaction.response.send_message(f"You're in voice with: {', '.join(member_names)}", ephemeral=True)
        
    async def cog_load(self):
        self.bot.tree.add_command(self.giveHomework, guild=settings.TRAIN_GUILD_ID)

async def setup(bot):
    await bot.add_cog(TrainCog(bot))
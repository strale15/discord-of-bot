from discord.ext import commands
from discord import app_commands, Interaction
import settings
import discord
from util import *
from classes import voice

class VoiceSubmitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ### VOICE ###
    @app_commands.command(name="voice", description="Submit voice for review")
    async def submitVoice(self, interaction: discord.Interaction):
        if not interaction.channel.name.lower().__contains__("-staff-chat"):
            await interaction.response.send_message(f"_Please submit voice in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        await interaction.response.send_modal(voice.VoiceModal())
        
    async def cog_load(self):
        self.bot.tree.add_command(self.submitVoice, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(VoiceSubmitCog(bot))
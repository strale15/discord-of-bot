from discord.ext import commands
from discord import app_commands
import settings
import discord
from util import *
from classes import massmsg

class MMACog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="mma", description="Submit MM for approval")
    async def submitMma(self, interaction: discord.Interaction):
        if not interaction.channel.name.lower().__contains__("-staff-chat"):
            await interaction.response.send_message(f"_Please submit mms in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        await interaction.response.send_modal(massmsg.MassMessageModal())
    
    async def cog_load(self):
        self.bot.tree.add_command(self.submitMma, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(MMACog(bot))
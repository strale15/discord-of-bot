from discord.ext import commands
from discord import app_commands
import settings
import discord
from util import *
from classes import leaks

class LeaksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ### LEAKS ###
    @app_commands.command(name="leaks", description="Submit a leak")
    async def submitLeak(self, interaction: discord.Interaction):
        if not interaction.channel.name.lower().__contains__("-staff-chat"):
            await interaction.response.send_message(f"_Please submit leak in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        await interaction.response.send_modal(leaks.LeakModal())
        
    async def cog_load(self):
        self.bot.tree.add_command(self.submitLeak, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(LeaksCog(bot))
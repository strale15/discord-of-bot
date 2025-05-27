import discord
from discord.ext import commands
from discord import app_commands

import settings
from util import *
from classes import customs

class CustomCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ### CUSTOMS ###
    @app_commands.command(name="cs", description="Submit custom for review")
    async def submitCustom(self, interaction: discord.Interaction):
        if not interaction.channel.name.lower().__contains__("-customs"):
            await interaction.response.send_message(f"_Please submit cs in customs model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        await interaction.response.send_modal(customs.CustomsModal())
        
    async def cog_load(self):
        self.bot.tree.add_command(self.submitCustom, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(CustomCog(bot))
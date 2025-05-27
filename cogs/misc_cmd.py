import discord
from discord.ext import commands
from discord import app_commands

import settings
from util import *
from classes import formats

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hi! Latency: {self.bot.latency}", ephemeral=True)
        
    #Format command
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(name="format", description="Makes a nicely formatted message")
    async def format(self, interaction: discord.Interaction):
        await interaction.response.send_modal(formats.FormatModal())
                
    #Create role - helper
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.command(name="c-role", description="Creates role and user to it")
    async def createRole(self, interaction: discord.Interaction, role_name: str):
        modelRole = getRoleByName(interaction.guild, role_name)
        if modelRole is None:
            modelRole = await interaction.guild.create_role(name=role_name, color=discord.Colour.random())
            
        await interaction.user.add_roles(modelRole)
        await interaction.response.send_message(f"You received the role {role_name}", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
    async def cog_load(self):
        self.bot.tree.add_command(self.ping, guilds=[settings.GUILD_ID, settings.M_GUILD_ID, settings.TRAIN_GUILD_ID, settings.ANNOUNCEMENT_GUILD_ID])
        self.bot.tree.add_command(self.createRole, guild=settings.GUILD_ID)
        self.bot.tree.add_command(self.format, guilds=[settings.GUILD_ID, settings.M_GUILD_ID, settings.TRAIN_GUILD_ID])

async def setup(bot):
    await bot.add_cog(Misc(bot))
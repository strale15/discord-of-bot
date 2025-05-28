import discord
from discord.ext import commands
from discord import app_commands

import settings
from util import *
from classes import fine, sheets

class FinesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ### FINES ###
    @app_commands.command(name="my-fines", description="Shows the list of your fines")
    async def showSelfFines(self, interaction: discord.Interaction):
        if not interaction.channel.name.lower().__contains__("fines"):
            await interaction.response.send_message(f"_Please use the command in the fines channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        fines = sheets.getUserFines(interaction.user.name)
        message = "_You don't have any fines (yet 🙂)!_"
        deleteAfter = settings.DELETE_AFTER
        if fines != "":
            message = fines
            deleteAfter = 300
        await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(name="fines", description="Shows the list of fines for given user, provide discord nick")
    async def showFineForUser(self, interaction: discord.Interaction, username: str):
        if not interaction.channel.name.lower().__contains__("fines"):
            await interaction.response.send_message(f"_Please use the command in the fines channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        fines = sheets.getUserFines(username)
        message = "_That user doesn't have any fines (yet 🙂)!_"
        deleteAfter = settings.DELETE_AFTER
        if fines != "":
            message = fines
            deleteAfter = 300
        await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)
    
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.default_permissions(manage_channels=True) 
    @app_commands.command(name="fine", description="Opens a form to fine a user")
    async def fineUser(self, interaction: discord.Interaction):
        managementRole = getManagementRole(interaction)
        consultantRole = getConsultRole(interaction)
        
        userRole1 = interaction.user.get_role(managementRole.id)
        userRole2 = interaction.user.get_role(consultantRole.id)
        if userRole1 == None and userRole2 == None:
            await interaction.response.send_message(f"_You do not have a required role for this action._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        if not interaction.channel.name.lower().__contains__("fines"):
            await interaction.response.send_message(f"_Please use the command in the fines channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        await interaction.response.send_modal(fine.FineModal())
        
    async def cog_load(self):
        self.bot.tree.add_command(self.showSelfFines, guild=settings.GUILD_ID)
        self.bot.tree.add_command(self.showFineForUser, guild=settings.GUILD_ID)
        self.bot.tree.add_command(self.fineUser, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(FinesCog(bot))
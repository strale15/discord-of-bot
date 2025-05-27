from discord.ext import commands
from discord import app_commands
import settings
import discord
from util import *
from classes import sheets

class ReferralsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ### REFERRALS ###
    @app_commands.command(name="my-referrals", description="Shows the list of you referrals")
    async def ShowSelfReferrals(self, interaction: discord.Interaction):
        referrals = sheets.getUserReferrals(interaction.user.name)
        message = "_You don't have any referrals._"
        deleteAfter = settings.DELETE_AFTER
        if referrals != "":
            message = referrals
            deleteAfter = 300
        await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)
        
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(name="referrals", description="Shows the list of referrals for given user, provide discord nick")
    async def showReferralsForUser(self, interaction: discord.Interaction, username: str):
        referrals = sheets.getUserReferrals(username)
        message = "_That user doesn't have any referrals._"
        deleteAfter = settings.DELETE_AFTER
        if referrals != "":
            message = referrals
            deleteAfter = 300
        await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)
        
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(name="add-referral", description="Adds the referral to employee. Please provide employee discord nick and referral discord nick.")
    async def addReferral(self, interaction: discord.Interaction, employee_nick: str, referral_nick: str):
        await interaction.response.defer(ephemeral=True)  # Prevents interaction expiration
        
        managementRole = getManagementRole(interaction)
        consultantRole = getConsultRole(interaction)
        
        userRole1 = interaction.user.get_role(managementRole.id)
        userRole2 = interaction.user.get_role(consultantRole.id)
        
        if userRole1 is None and userRole2 is None:
            msg = await interaction.followup.send("_You do not have a required role for this action._")
            asyncio.create_task(delete_message_after_delay(msg, settings.DELETE_AFTER))
            return
        
        message = "_Problem adding a referral, please check the sheets._"
        if sheets.addReferral(employee_nick, referral_nick):
            message = f"_Added {referral_nick} successfully as a referral to {employee_nick}_"
        
        msg = await interaction.followup.send(message)
        asyncio.create_task(delete_message_after_delay(msg, settings.DELETE_AFTER))
        
    async def cog_load(self):
        self.bot.tree.add_command(self.ShowSelfReferrals, guild=settings.GUILD_ID)
        self.bot.tree.add_command(self.showReferralsForUser, guild=settings.GUILD_ID)
        self.bot.tree.add_command(self.addReferral, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(ReferralsCog(bot))
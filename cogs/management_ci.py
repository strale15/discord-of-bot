import discord
from discord.ext import commands
from discord import app_commands

import settings
from util import *

class ManagementCiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    ### MANAGEMENT CI/CO ###
    @app_commands.command(name="ci", description="Clocks you in")
    async def clockIn(self, interaction: discord.Interaction):
        if not interaction.channel.name.__contains__("clock-in"):
            await interaction.response.send_message(f"_Please use the clock in text channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        clockInChannel = getUserClockInChannel(interaction.user)
        if clockInChannel is None:
            await interaction.response.send_message(f"_You do not have any management type role._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
            
        #Add user to channel name
        if checkIfUserIsClockedIn(interaction.user, clockInChannel.name):
            await interaction.response.send_message(f"_You are already clocked in._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        username = interaction.user.display_name
        newChannelName = f"{clockInChannel.name}, {username}" if clockInChannel.name[-1] != '-' else f"{settings.TICK_EMOJI}{clockInChannel.name[1:]} {username}"
        
        status, wait_time = await renameChannelRateLimit(clockInChannel, newChannelName)
        if status is False:
            await interaction.response.send_message(f"Unable to ci/co now, please try again in **{wait_time} minutes.** [_Rate limited_]", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        await interaction.response.send_message(f"You are now clocked in", ephemeral=False)
        
    @app_commands.command(name="co", description="Clocks you out")
    async def clockOut(self, interaction: discord.Interaction):
        if not interaction.channel.name.__contains__("clock-in"):
            await interaction.response.send_message(f"_Please use the clock in text channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        clockInChannel = getUserClockInChannel(interaction.user)
        if clockInChannel is None:
            await interaction.response.send_message(f"_You do not have any management type role._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        if not checkIfUserIsClockedIn(interaction.user, clockInChannel.name):
            await interaction.response.send_message(f"_You are already clocked out._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        username = interaction.user.display_name
        
        usernames = getClockedInUsernames(clockInChannel.name)
        usernames.remove(username)
        
        if len(usernames) == 0:
            newChannelName = settings.CROSS_EMOJI + getBaseChannelName(clockInChannel.name)[1:] + " -"
        else:
            newChannelName = getBaseChannelName(clockInChannel.name) + " - " + ', '.join(usernames)
            
        status, wait_time = await renameChannelRateLimit(clockInChannel, newChannelName)
        if status is False:
            await interaction.response.send_message(f"Unable to ci/co now, please try again in **{wait_time} minutes.** [_Rate limited_]", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        await interaction.response.send_message(f"You are now clocked out", ephemeral=False)
        
    async def cog_load(self):
        self.bot.tree.add_command(self.clockIn, guild=settings.M_GUILD_ID)
        self.bot.tree.add_command(self.clockOut, guild=settings.M_GUILD_ID)

async def setup(bot):
    await bot.add_cog(ManagementCiCog(bot))
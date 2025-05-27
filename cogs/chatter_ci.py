import discord
from discord import app_commands, Interaction
from discord.ext import commands
import asyncio

import settings
from util import *
from classes import database

log = settings.logging.getLogger()


# =========================
# EXTERNAL COMMAND HANDLERS
# =========================

@app_commands.command(name="ci", description="Clocks you in. Use in model text channel to clock in for that model.")
async def ciCommand(interaction: Interaction):
    await interaction.response.defer(ephemeral=False)

    if interaction.channel.category is None:
        message = await interaction.followup.send("_Wrong channel, use one of the model text channels._")
        asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
        return

    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name

    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower():
            if checkIfUserIsClockedIn(interaction.user, channel.name):
                message = await interaction.followup.send("_You are already clocked in._", ephemeral=True)
                asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
                return

            newChannelName = f"{channel.name}, {username}" if channel.name[-1] != '-' else f"{settings.TICK_EMOJI}{channel.name[1:]} {username}"
            await channel.edit(name=newChannelName)

            if not database.is_mma_grace_period_on(user_id=interaction.user.id, model_channel_id=interaction.channel_id):
                database.insert_ping(chatter_id=interaction.user.id, model_channel_id=interaction.channel_id)

            await interaction.followup.send(f"You are now clocked in _{modelName}_.")
            return

    message = await interaction.followup.send("_Model is missing the voice channel, please create one using /setup._")
    asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))


@ciCommand.error
async def ci_error(interaction: Interaction, error: app_commands.AppCommandError):
    if "RateLimited" in str(error):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking in!_", ephemeral=True, delete_after=settings.DELETE_AFTER)


@app_commands.command(name="co", description="Clocks you out. Use in model text channel to clock out for that model.")
async def coCommand(interaction: Interaction):
    await interaction.response.defer(ephemeral=False)

    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name

    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower() and checkIfUserIsClockedIn(interaction.user, channel.name):
            usernames = getClockedInUsernames(channel.name)
            usernames.remove(username)

            if len(usernames) == 0:
                newChannelName = settings.CROSS_EMOJI + getBaseChannelName(channel.name)[1:] + " -"
            else:
                newChannelName = getBaseChannelName(channel.name) + " - " + ', '.join(usernames)

            await channel.edit(name=newChannelName)

            message = await interaction.followup.send(f"You are now clocked out of _{modelName}_.", ephemeral=False)
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
            return

    message = await interaction.followup.send("_You are not clocked in on any model._", ephemeral=True)
    asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))


@coCommand.error
async def co_error(interaction: Interaction, error: app_commands.AppCommandError):
    if "RateLimited" in str(error):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking out!_", ephemeral=True, delete_after=settings.DELETE_AFTER)


@app_commands.command(name="co-all", description="Clocks everyone from VC. Use in model text channel to clock everyone out.")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
async def coallCommand(interaction: Interaction):
    await interaction.response.send_message("Processing, please wait...")

    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')

    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower():
            newChannelName = settings.CROSS_EMOJI + getBaseChannelName(channel.name)[1:] + " -"
            await channel.edit(name=newChannelName)

    message = await interaction.followup.send(f"_Everyone is now clocked out from {modelName}._", ephemeral=True)
    asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))


@coallCommand.error
async def coall_error(interaction: Interaction, error: app_commands.AppCommandError):
    if "RateLimited" in str(error):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking everyone out!_", ephemeral=True, delete_after=settings.DELETE_AFTER)


# =====================
# COG DEFINITION & SETUP
# =====================

class ChatterCiCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(ciCommand, guild=settings.GUILD_ID)
        self.bot.tree.add_command(coCommand, guild=settings.GUILD_ID)
        self.bot.tree.add_command(coallCommand, guild=settings.GUILD_ID)


async def setup(bot):
    await bot.add_cog(ChatterCiCog(bot))
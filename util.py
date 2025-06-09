import dis
import math
import discord
import settings
import asyncio
from pathlib import Path
import json

log = settings.logging.getLogger()
img_id_drive_id_dict_path="resources/training/ctx_imgs_drive_ids.json"

def getUserClockInChannel(user: discord.Member) -> discord.VoiceChannel:
    guild = user.guild
    userRoles = user.roles
    
    consultantRole = guild.get_role(settings.M_CONSULTANT_ROLE_ID)
    managementRole = guild.get_role(settings.M_MANAGEMENT_ROLE_ID)
    supervisorRole = guild.get_role(settings.M_SUPERVISOR_ROLE_ID)
    ppvEngRole = guild.get_role(settings.M_PPV_ENG_ROLE_ID)
    
    consultantChannel = guild.get_channel(settings.M_CONSULTANT_CLOCK_CHANNEL)
    managementChannel = guild.get_channel(settings.M_MANAGEMENT_CLOCK_CHANNEL)
    supervisorChannel = guild.get_channel(settings.M_SUPERVISOR_CLOCK_CHANNEL)
    ppvEngChannel = guild.get_channel(settings.M_PPV_ENG_CLOCK_CHANNEL)
    
    if consultantRole in userRoles:
        return consultantChannel
    elif managementRole in userRoles:
        return managementChannel
    elif supervisorRole in userRoles:
        return supervisorChannel
    elif ppvEngRole in userRoles:
        return ppvEngChannel
    else:
        return None

def getCategoryByName(guild: discord.Guild, categoryName: str) -> discord.CategoryChannel:
    for category in guild.categories:
        if category.name.lower().__contains__(categoryName.lower()):
            return category
    return None

def getRoleByName(guild: discord.Guild, name: str) -> discord.Role:
    for role in guild.roles:
        if role.name.lower().__contains__(name.lower()):
            return role
    return None

def getClockedInUsernames(channelName: str) -> list:
    if channelName[-1] == '-':
        return None
    
    allUsers = channelName.split('-')[1].strip()
    usernames = allUsers.split(',')
    return [username.strip() for username in usernames]

def checkIfUserIsClockedIn(user: discord.Member, channelName: str) -> bool:
    clockedInUsers = getClockedInUsernames(channelName)
    if clockedInUsers is None:
        return False
    
    return user.display_name in clockedInUsers

#Takes user id and model text channel id to see if that user is clocked into that model
def checkIfUserIsClockedInByIds(interaction: discord.Interaction, user_id, model_channel_id):
    user = discord.utils.get(interaction.guild.members, id=user_id)
    model_text_channel = discord.utils.get(interaction.guild.channels, id=model_channel_id)
    
    modelName = model_text_channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = user.display_name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower():
            if checkIfUserIsClockedIn(user, channel.name):
                return True
            
    return False

def getBaseChannelName(channelName: str) -> str:
    return channelName.split('-')[0].strip()

def getMemberByUser(interaction: discord.Interaction, userId: int) -> discord.Member:
    return interaction.guild.get_member(userId)

def getMmaApprovalChannel(interaction: discord.Interaction) -> discord.TextChannel:
    return discord.utils.get(interaction.guild.channels, id=settings.MMA_APPROVAL_ID)
    
def getCsApprovalChannel(interaction: discord.Interaction) -> discord.TextChannel:
    return discord.utils.get(interaction.guild.channels, id=settings.CUSTOMS_QUEUE_ID)

def getVoiceQueueChannel(interaction: discord.Interaction) -> discord.TextChannel:
    return discord.utils.get(interaction.guild.channels, id=settings.VOICE_QUEUE_ID)
    
def getLeaksChannel(interaction: discord.Interaction) -> discord.TextChannel:
    return discord.utils.get(interaction.guild.channels, id=settings.LEAKS_QUEUE_ID)
    
def getConsultRole(interaction: discord.Interaction) -> discord.Role:
    return discord.utils.get(interaction.guild.roles, id=settings.CONSULT_ROLE_ID)
    
def getManagementRole(interaction: discord.Interaction) -> discord.Role:
    return discord.utils.get(interaction.guild.roles, id=settings.MANAGEMENT_ROLE_ID)
    
def getSupervisorRole(interaction: discord.Interaction) -> discord.Role:
    return discord.utils.get(interaction.guild.roles, id=settings.SUPERVISOR_ROLE_ID)
    
def getPPVEngRole(interaction: discord.Interaction) -> discord.Role:
    return discord.utils.get(interaction.guild.roles, id=settings.PPV_ENG_ROLE_ID)

async def remove_role_by_ids(bot, guild_id: int, user_id: int, role_id: int):
    guild = await bot.fetch_guild(guild_id)
    if not guild:
        log.warning("Guild not found!")
        return False

    user = await guild.fetch_member(user_id)
    if not user:
        log.warning(f"User with id {user_id} not found in guild with id {guild}!")
        return False

    role = guild.get_role(role_id)
    if not role:
        log.warning(f"Role with id:{role_id} not found!")
        return False

    try:
        await user.remove_roles(role)
        log.info(f"Removed role {role.name} from {user.name}!")
        return True
    except Exception as e:
        log.warning(e)
        return False
    
async def assign_role_by_ids(bot, guild_id: int, user_id: int, role_id: int):
    guild = await bot.fetch_guild(guild_id)
    if not guild:
        log.warning(f"Guild with id {guild_id} not found!")
        return False

    user = await guild.fetch_member(user_id)
    if not user:
        log.warning(f"User with id {user_id} not found in guild with id {guild}!")
        return False

    role = guild.get_role(role_id)
    if not role:
        log.warning(f"Role with id:{role_id} not found!")
        return False

    try:
        await user.add_roles(role)
        log.info(f"Assigned role {role.name} to {user.name}!")
        return True
    except Exception as e:
        log.warning(e)
        return False
    
async def delete_message_after_delay(message: discord.Message, delay: int):
    await asyncio.sleep(delay)
    await delete_message_ignore_exception(message)
    
async def delete_message_ignore_exception(message: discord.Message, source: str=None):
    try:
        await message.delete()
    except:
        try:
            fetched_message = await message.channel.fetch_message(message.id)
            await fetched_message.delete()
        except Exception as e:
            if source is not None:
                log.warning(f"Failed to delete message with id {message.id} ({source}): {e}")
            #ignore exception
            pass
    
async def renameChannelRateLimit(channel: discord.VoiceChannel, newName: str):
    try:
        await asyncio.wait_for(channel.edit(name=newName), timeout=7.0)
        return True, 0.0
    except (asyncio.TimeoutError, discord.HTTPException):
        return False, 10.0
    
def countContextImages() -> int:
    try:
        with open(img_id_drive_id_dict_path, "r") as f:
            mapping = json.load(f)
        return len(mapping)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def getCtxImgDriveId(img_id):
    try:
        with open(img_id_drive_id_dict_path, "r") as f:
            mapping = json.load(f)
        return mapping.get(f"{img_id}.png")
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    
async def get_train_guild_display_name_from_user_id(bot, user_id: int) -> str:
    guild = bot.get_guild(settings.TRAIN_GUILD_ID_INT)
    if not guild:
        guild = await bot.fetch_guild(settings.TRAIN_GUILD_ID_INT)
    try:
        member = guild.get_member(user_id) or await guild.fetch_member(user_id)
        return member.display_name
    except Exception as e:
        log.error(e)
        return "Unknown User"
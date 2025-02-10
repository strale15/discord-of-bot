import discord
import settings

def getCategoryByName(guild: discord.Guild, categoryName: str) -> discord.CategoryChannel:
    for category in guild.categories:
        if category.name.lower() == categoryName.lower():
            return category
    return None

def getRoleByName(guild: discord.Guild, name: str) -> discord.Role:
    for role in guild.roles:
        if role.name.lower() == name.lower():
            return role
    return None

def getClockedInUsernames(channelName: str) -> list:
    if channelName[-1] == '-':
        return None
    
    allUsers = channelName.split('-')[1].strip()
    usernames = allUsers.split(',')
    return [username.strip() for username in usernames]

def getBaseChannelName(channelName: str) -> str:
    return channelName.split('-')[0].strip()

def getMember(interaction: discord.Interaction) -> discord.Member:
    return interaction.guild.get_member(interaction.user.id)

def getMemberByUser(interaction: discord.Interaction, userId: int) -> discord.Member:
    return interaction.guild.get_member(userId)

def getMmaApprovalChannel(interaction: discord.Interaction) -> discord.TextChannel:
    if interaction.guild_id == settings.GUILD_ID_INT_DEV:
        return discord.utils.get(interaction.guild.channels, id=settings.MMA_APPROVAL_ID_DEV)
    elif interaction.guild_id == settings.GUILD_ID_INT_PROD:
        return discord.utils.get(interaction.guild.channels, id=settings.MMA_APPROVAL_ID_PROD)
    else:
        return None
    
def getCsApprovalChannel(interaction: discord.Interaction) -> discord.TextChannel:
    if interaction.guild_id == settings.GUILD_ID_INT_DEV:
        return discord.utils.get(interaction.guild.channels, id=settings.CUSTOMS_QUEUE_ID_DEV)
    elif interaction.guild_id == settings.GUILD_ID_INT_PROD:
        return discord.utils.get(interaction.guild.channels, id=settings.CUSTOMS_QUEUE_ID_PROD)
    else:
        return None

def getVoiceQueueChannel(interaction: discord.Interaction) -> discord.TextChannel:
    if interaction.guild_id == settings.GUILD_ID_INT_DEV:
        return discord.utils.get(interaction.guild.channels, id=settings.VOICE_QUEUE_ID_DEV)
    elif interaction.guild_id == settings.GUILD_ID_INT_PROD:
        return discord.utils.get(interaction.guild.channels, id=settings.VOICE_QUEUE_ID_PROD)
    else:
        return None
    
def getLeaksChannel(interaction: discord.Interaction) -> discord.TextChannel:
    if interaction.guild_id == settings.GUILD_ID_INT_DEV:
        return discord.utils.get(interaction.guild.channels, id=settings.LEAKS_QUEUE_ID_DEV)
    elif interaction.guild_id == settings.GUILD_ID_INT_PROD:
        return discord.utils.get(interaction.guild.channels, id=settings.LEAKS_QUEUE_ID_PROD)
    else:
        return None
    
def getConsultRole(interaction: discord.Interaction) -> discord.Role:
    if interaction.guild_id == settings.GUILD_ID_INT_DEV:
        return discord.utils.get(interaction.guild.roles, id=settings.CONSULT_ID_DEV)
    elif interaction.guild_id == settings.GUILD_ID_INT_PROD:
        return discord.utils.get(interaction.guild.roles, id=settings.CONSULT_ID_PROD)
    else:
        return None
    
def getSupervisorRole(interaction: discord.Interaction) -> discord.Role:
    if interaction.guild_id == settings.GUILD_ID_INT_DEV:
        return discord.utils.get(interaction.guild.roles, id=settings.SUPERVISOR_ID_DEV)
    elif interaction.guild_id == settings.GUILD_ID_INT_PROD:
        return discord.utils.get(interaction.guild.roles, id=settings.SUPERVISOR_ID_PROD)
    else:
        return None
    
def getPPVEngRole(interaction: discord.Interaction) -> discord.Role:
    if interaction.guild_id == settings.GUILD_ID_INT_DEV:
        return discord.utils.get(interaction.guild.roles, id=settings.PPV_ENG_ID_DEV)
    elif interaction.guild_id == settings.GUILD_ID_INT_PROD:
        return discord.utils.get(interaction.guild.roles, id=settings.PPV_ENG_ID_PROD)
    else:
        return None
    
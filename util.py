import dis
import discord
import settings

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
    return discord.utils.get(interaction.guild.roles, id=settings.CONSULT_ID)
    
def getManagementRole(interaction: discord.Interaction) -> discord.Role:
    return discord.utils.get(interaction.guild.roles, id=settings.MANAGEMENT_ROLE_ID)
    
def getSupervisorRole(interaction: discord.Interaction) -> discord.Role:
    return discord.utils.get(interaction.guild.roles, id=settings.SUPERVISOR_ID)
    
def getPPVEngRole(interaction: discord.Interaction) -> discord.Role:
    return discord.utils.get(interaction.guild.roles, id=settings.PPV_ENG_ID)
    
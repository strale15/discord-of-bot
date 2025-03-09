import discord
import settings

def findChannelsByNameInCategory(category: discord.CategoryChannel, username: str) -> list[discord.TextChannel]:
    channels = []
    username = username.replace(" ", "-").lower()
    
    for channel in category.channels:
        if channel.name.lower().__contains__(username):  # Case-insensitive search
            channels.append(channel)
            
    if len(channels) == 0:
        return None
    
    return channels

def interactionChannelContainsUserName(interaction: discord.Interaction) -> bool:
    username = interaction.user.display_name.replace(" ", "-").lower()
    return interaction.channel.name.lower().__contains__(username)

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

def getBaseChannelName(channelName: str) -> str:
    return channelName.split('-')[0].strip()

def getMember(interaction: discord.Interaction) -> discord.Member:
    return interaction.guild.get_member(interaction.user.id)

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
    
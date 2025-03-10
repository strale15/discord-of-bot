import discord
import settings

async def findClockInChannelByUsername(guild: discord.Guild, username: str) -> discord.TextChannel:
    username = username.replace(" ", "-").lower()
    
    channelsToCheck = await getAllManagementClockInCategories(guild)
    
    for channel in channelsToCheck:
        if channel.name[:-2].lower() == (username):
            return channel
            
    return None

async def getAllManagementClockInCategories(guild: discord.Guild):
    supervisor_category = await guild.fetch_channel(settings.M_SUPERVISOR_CLOCK_CATEGORY)
    consultant_category = await guild.fetch_channel(settings.M_CONSULTANT_CLOCK_CATEGORY)
    management_category = await guild.fetch_channel(settings.M_MANAGEMENT_CLOCK_CATEGORY)
    mppv_category = await guild.fetch_channel(settings.M_MPPV_ENG_CLOCK_CATEGORY)
    
    return supervisor_category.channels + consultant_category.channels + management_category.channels + mppv_category.channels

def interactionChannelContainsUserName(interaction: discord.Interaction) -> bool:
    username = interaction.user.display_name.replace(" ", "-").lower()
    return interaction.channel.name[:-2].lower() == (username)

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
    
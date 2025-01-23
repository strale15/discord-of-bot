import discord

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
    usernames = allUsers.split('+')
    return [username.strip() for username in usernames]

def getBaseChannelName(channelName: str) -> str:
    return channelName.split('-')[0].strip()
    
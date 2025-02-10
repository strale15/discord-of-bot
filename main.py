import discord
from discord.ext import commands
from discord import HTTPException, app_commands

import settings
from classes import massmsg, customs, formats
from util import *
import util
class MyClient(commands.Bot):
    async def on_ready(self):
        log.info(f'Logged on as {self.user}!')
        
        try:
            syncedDev = await self.tree.sync(guild=settings.GUILD_ID_DEV)
            syncedProd = await self.tree.sync(guild=settings.GUILD_ID_PROD)
            log.info(f'Synced {len(syncedDev)} on dev and {len(syncedProd)} commands on prod!')        
        except Exception as e:
            log.info(f"Sync failed {e}")
            
#SETUP BOT
log = settings.logging.getLogger()
    
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(command_prefix="!", intents=intents, max_ratelimit_timeout=90)

###---------------- COMMANDS ----------------###
            
#Global error handling        
@client.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    log.error(f"Error : {error}")
    #await interaction.response.send_message(f'Error global: ({error})', ephemeral=True)
       
@client.tree.command(name="test", description="Performs a sanity check.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def testSanity(interaction: discord.Interaction):
    await interaction.response.send_message(f"*Hi!* Everything seems to work properly 😊 (everything is configured, latency - {client.latency})", ephemeral=True)
    
@client.tree.command(name="test-param", description="Performs a param check.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def testSanity(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text, ephemeral=True)
    
# Format command
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="format", description="Makes a nicely formatted message", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def multiline(interaction: discord.Interaction):
    await interaction.response.send_modal(formats.FormatModal())
        
#Setup command
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="setup", description="Creates voice channel in 'clock in' based on the model category", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def setupClockInChannel(interaction: discord.Interaction):
    if interaction.channel.category is None:
        await interaction.response.send_message(f"_Please use the command in appropriate model text channel._", ephemeral=True)
        return
        
    modelName = interaction.channel.category.name
    
    clockInCategory = getCategoryByName(interaction.guild, "clock in")
    if clockInCategory is None:
        await interaction.response.send_message(f"_'Clock in' category' does not exist, please create it._", ephemeral=True)
        return
    
    for voice in clockInCategory.voice_channels:
        if voice.name.lower().__contains__(modelName.lower()):
            await interaction.response.send_message(f"_Model voice channel is already setup._", ephemeral=True)
            return
    
    modelRole = getRoleByName(interaction.guild, modelName)
    if modelRole is None:
        await interaction.response.send_message(f"_{modelName} role does not exist, please create it._", ephemeral=True)
        return
    
    supervisorRole = util.getSupervisorRole(interaction)
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
                    supervisorRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                }
    
    try:
        createdChannel = await interaction.guild.create_voice_channel("❌" + modelName + " -", category=clockInCategory, overwrites=overwrites)
        await interaction.response.send_message(f"_Successfully created {createdChannel.name} vc!_", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True)
        
#Recruit command - helper
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, model_name: str):
    alreadyExistingCategory = getCategoryByName(interaction.guild, model_name)
    if alreadyExistingCategory is not None:
        await interaction.response.send_message(f"_{model_name} category is already setup!_", ephemeral=True)
        return
    
    modelRole = getRoleByName(interaction.guild, model_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=model_name, color=discord.Colour.magenta())
        
    ppvRole = util.getPPVEngRole(interaction)
    supervisorRole = util.getSupervisorRole(interaction)
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
                    ppvRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
                    supervisorRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                }
    
    try:
        createdCategory = await interaction.guild.create_category(model_name, overwrites=overwrites)
        await interaction.guild.create_text_channel("💬-staff-chat", category=createdCategory)
        await interaction.guild.create_text_channel("📰-info", category=createdCategory)
        await interaction.guild.create_text_channel("📷-customs", category=createdCategory)
        await interaction.response.send_message(f"_Successfully created {model_name} model space, you can now use /setup in staff chat to create clock in vc!_", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True)
        
#Clean model info
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="delete-model-info", description="Deletes all model info (categories, channels, role)", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, model_name: str):
    model_name = model_name.lower()
    
    try:
        #Remove model category
        allCategories = interaction.guild.categories
        for category in allCategories:
            if category.name.lower().__contains__(model_name):
                for channel in category.channels:
                        await channel.delete()
                await category.delete()
                
        #Remove model vc
        allChannels = interaction.guild.channels
        for channel in allChannels:
            if channel.name.lower().__contains__(model_name):
                await channel.delete()
                
        modelRole = getRoleByName(interaction.guild, model_name)
        if modelRole is not None:
            await modelRole.delete()
            
        await interaction.response.send_message(f"Successfully deleted all {model_name} info!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete model info: {e}", ephemeral=True)
        
#Create role - helper
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="c-role", description="Creates role and user to it", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=role_name, color=discord.Colour.random())
        
    await interaction.user.add_roles(modelRole)
    await interaction.response.send_message(f"You received the role {role_name}", ephemeral=True)
    
#Delete role
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="d-role", description="Deletes a role", guilds=[settings.GUILD_ID_DEV])
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        await interaction.response.send_message(f"_Role {role_name} does not exist!_", ephemeral=True)
        
    await modelRole.delete()
    await interaction.response.send_message(f"_{role_name} deleted!_ 🚮", ephemeral=True)
        
#Clock in command
@client.tree.command(name="ci", description="Clocks you in. Use in model text channel to clock in for that model.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def ciCommand(interaction: discord.Interaction):
    if interaction.channel.category is None:
        await interaction.response.send_message(f"_Wrong channel, use one of the model text channels._")
        return
    
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and channel.name.lower().__contains__(modelName):
            if channel.name.__contains__(username):
                await interaction.response.send_message(f"_You are already clocked in._", ephemeral=True)
                return
            
            if channel.name[-1] != '-':
                newChannelName = channel.name + ", " + username
            else:
                newChannelName = "✅" + channel.name[1:] + " " + username
              
            await channel.edit(name=newChannelName)  
            await interaction.response.send_message(f"You are now clocked in! Good luck soldier 🫡", ephemeral=True)
            return
        
    await interaction.response.send_message(f"_Model is missing the voice channel, please create one using /setup._", ephemeral=True)
    
@ciCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking in!_", ephemeral=True)
    
#Clock out command
@client.tree.command(name="co", description="Clocks you out. Use in model text channel to clock out for that model.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def coCommand(interaction: discord.Interaction):
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and channel.name.lower().__contains__(modelName):
            if channel.name.__contains__(username):
                #remove username from channel.name string
                usernames = getClockedInUsernames(channel.name)
                usernames.remove(username)
                
                if len(usernames) == 0:
                    newChannelName = "❌" + getBaseChannelName(channel.name)[1:] + " -"
                else:
                    newChannelName = getBaseChannelName(channel.name) + " - " + ', '.join(usernames)
                    
                await channel.edit(name=newChannelName)
                await interaction.response.send_message("_You are now clocked out._", ephemeral=True)
                return
            
    await interaction.response.send_message(f"_You are not clocked in on any model._", ephemeral=True)
    
@coCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking out!_", ephemeral=True)
        
#Clock out everyone
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="co-all", description="Clocks everyone from vc. Use in model text channel to clock everyone out for that model.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def coallCommand(interaction: discord.Interaction):
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and channel.name.lower().__contains__(modelName):
            newChannelName = "❌" + getBaseChannelName(channel.name)[1:] + " -"
            await channel.edit(name=newChannelName)
            await interaction.response.send_message(f"_Everyone is now clocked out from {modelName}._", ephemeral=True)
            return
                          
    await interaction.response.send_message(f"_Error occurred._", ephemeral=True)
    
@coallCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking everyone out!_", ephemeral=True)
    
### MMA ###
@client.tree.command(name="mma", description="Submit MM for approval", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-staff-chat"):
        await interaction.response.send_message(f"_Please submit mms in staff chat model channel._", ephemeral=True)
        return
    await interaction.response.send_modal(massmsg.MassMessageModal())
    
### CUSTOMS ###
@client.tree.command(name="cs", description="Submit custom for approval", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-customs"):
        await interaction.response.send_message(f"_Please submit cs in customs model channel._", ephemeral=True)
        return
    await interaction.response.send_modal(customs.CustomsModal())

        
#RUN BOT     
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
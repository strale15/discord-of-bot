import datetime
from email.mime import message
import discord
from discord.ext import commands
from discord import HTTPException, app_commands
import asyncio

import settings
from classes import massmsg, customs, formats, voice, leaks, sheets, fine
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
    
intents = discord.Intents.all()
intents.message_content = True

client = MyClient(command_prefix="!", intents=intents)

###---------------- COMMANDS ----------------###
            
#Global error handling        
@client.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    log.error(f"Error : {error}")
    #await interaction.response.send_message(f'Error global: ({error})', ephemeral=True, delete_after=settings.DELETE_AFTER)
       
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="ping", description="Check bot latency.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def testSanity(interaction: discord.Interaction):
    await interaction.response.send_message(f"*Hi!* Everything seems to work properly 😊 (everything is configured, latency - {client.latency})", ephemeral=True, delete_after=settings.DELETE_AFTER)
    
@client.tree.command(name="test-param", description="Performs a param check.", guilds=[settings.GUILD_ID_DEV])
async def testSanity(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text, ephemeral=True, delete_after=settings.DELETE_AFTER)
    
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
        await interaction.response.send_message(f"_Please use the command in appropriate model text channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
        
    modelName = interaction.channel.category.name
    
    clockInCategory = getCategoryByName(interaction.guild, "clock in")
    if clockInCategory is None:
        await interaction.response.send_message(f"_'Clock in' category' does not exist, please create it._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    for voice in clockInCategory.voice_channels:
        if voice.name.lower().__contains__(modelName.lower()):
            await interaction.response.send_message(f"_Model voice channel is already setup._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
    
    modelRole = getRoleByName(interaction.guild, modelName)
    if modelRole is None:
        await interaction.response.send_message(f"_{modelName} role does not exist, please create it._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    supervisorRole = util.getSupervisorRole(interaction)
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True),
                    supervisorRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                }
    
    try:
        createdChannel = await interaction.guild.create_voice_channel("❌" + modelName + " -", category=clockInCategory, overwrites=overwrites)
        await interaction.response.send_message(f"_Successfully created {createdChannel.name} vc!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
#Recruit command - helper
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, model_name: str):
    alreadyExistingCategory = getCategoryByName(interaction.guild, model_name)
    if alreadyExistingCategory is not None:
        await interaction.response.send_message(f"_{model_name} category is already setup!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    roleName = f"Team {model_name}"
    modelRole = getRoleByName(interaction.guild, roleName)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=roleName, color=discord.Colour.magenta())
        
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
        await interaction.guild.create_text_channel(f"💬-{model_name}-staff-chat", category=createdCategory)
        await interaction.guild.create_text_channel(f"📰-{model_name}-info", category=createdCategory)
        await interaction.guild.create_text_channel(f"📷-{model_name}-customs", category=createdCategory)
        await interaction.response.send_message(f"_Successfully created {model_name} model space, you can now use /setup in staff chat to create clock in vc!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
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
            
        await interaction.response.send_message(f"Successfully deleted all {model_name} info!", ephemeral=True, delete_after=settings.DELETE_AFTER)
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete model info: {e}", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
#Create role - helper
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="c-role", description="Creates role and user to it", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=role_name, color=discord.Colour.random())
        
    await interaction.user.add_roles(modelRole)
    await interaction.response.send_message(f"You received the role {role_name}", ephemeral=True, delete_after=settings.DELETE_AFTER)
    
#Delete role
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="d-role", description="Deletes a role", guilds=[settings.GUILD_ID_DEV])
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        await interaction.response.send_message(f"_Role {role_name} does not exist!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
    await modelRole.delete()
    await interaction.response.send_message(f"_{role_name} deleted!_ 🚮", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
@client.tree.command(
    name="ci", 
    description="Clocks you in. Use in model text channel to clock in for that model.", 
    guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD]
)
async def ciCommand(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)  # Prevents interaction expiration

    if interaction.channel.category is None:
        await interaction.followup.send(f"_Wrong channel, use one of the model text channels._")
        return
    
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower():
            if username in channel.name:
                await interaction.followup.send(f"_You are already clocked in._", ephemeral=True, delete_after=settings.DELETE_AFTER)
                return
            
            newChannelName = f"{channel.name}, {username}" if channel.name[-1] != '-' else f"✅{channel.name[1:]} {username}"
            await channel.edit(name=newChannelName)

            try:
                with open("clocklog.txt", "a") as file:
                    now = datetime.datetime.now()
                    datetime_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"CI [{datetime_string}] - username: {interaction.user.name} - model: {modelName}\n")
            except:
                log.warning("Error logging ci to file")

            await interaction.followup.send(f"You are now clocked in _{modelName}_.")
            return
        
    await interaction.followup.send(f"_Model is missing the voice channel, please create one using /setup._", delete_after=settings.DELETE_AFTER)
    
@ciCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking in!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
    
@client.tree.command(
    name="co", 
    description="Clocks you out. Use in model text channel to clock out for that model.", 
    guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD]
)
async def coCommand(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)  # Prevents interaction expiration

    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and channel.name.lower().__contains__(modelName):
            if channel.name.__contains__(username):
                # Remove username from channel name
                usernames = getClockedInUsernames(channel.name)
                usernames.remove(username)
                
                if len(usernames) == 0:
                    newChannelName = "❌" + getBaseChannelName(channel.name)[1:] + " -"
                else:
                    newChannelName = getBaseChannelName(channel.name) + " - " + ', '.join(usernames)
                    
                await channel.edit(name=newChannelName)
                try:
                    with open("clocklog.txt", "a") as file:
                        now = datetime.datetime.now()
                        datetime_string = now.strftime("%Y-%m-%d %H:%M:%S")
                        file.write(f"CO [{datetime_string}] - username: {interaction.user.name} - model: {modelName}\n")
                except:
                    log.warning("Error logging co to file")
                
                await interaction.followup.send(f"You are now clocked out of _{modelName}_.")
                return
            
    await interaction.followup.send(f"_You are not clocked in on any model._", delete_after=settings.DELETE_AFTER)
    
@coCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking out!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
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
            await interaction.response.send_message(f"_Everyone is now clocked out from {modelName}._", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
                          
    await interaction.response.send_message(f"_Error occurred._", ephemeral=True, delete_after=settings.DELETE_AFTER)
    
@coallCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking everyone out!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
    
### MMA ###
@client.tree.command(name="mma", description="Submit MM for approval", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-staff-chat"):
        await interaction.response.send_message(f"_Please submit mms in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(massmsg.MassMessageModal())
    
### CUSTOMS ###
@client.tree.command(name="cs", description="Submit custom for review", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-customs"):
        await interaction.response.send_message(f"_Please submit cs in customs model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(customs.CustomsModal())
    
### VOICE ###
@client.tree.command(name="voice", description="Submit voice for review", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-staff-chat"):
        await interaction.response.send_message(f"_Please submit voice in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(voice.VoiceModal())
    
### LEAKS ###
@client.tree.command(name="leaks", description="Submit a leak", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-staff-chat"):
        await interaction.response.send_message(f"_Please submit leak in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(leaks.LeakModal())
    
### FINES ###
@client.tree.command(name="my-fines", description="Shows the list of you fines", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("fines"):
        await interaction.response.send_message(f"_Please use the command in the fines channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    fines = sheets.getUserFines(interaction.user.name)
    message = "_You don't have any fines (yet 🙂)!_"
    deleteAfter = settings.DELETE_AFTER
    if fines != "":
        message = fines
        deleteAfter = 300
    await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)

@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="fines", description="Shows the list of fines for given user, provide discord nick", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction, username: str):
    if not interaction.channel.name.lower().__contains__("fines"):
        await interaction.response.send_message(f"_Please use the command in the fines channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    fines = sheets.getUserFines(username)
    message = "_That user doesn't have any fines (yet 🙂)!_"
    deleteAfter = settings.DELETE_AFTER
    if fines != "":
        message = fines
        deleteAfter = 300
    await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)
   
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True) 
@client.tree.command(name="fine", description="Opens a form to fine a user", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    managementRole = util.getManagementRole(interaction)
    consultantRole = util.getConsultRole(interaction)
    
    userRole1 = interaction.user.get_role(managementRole.id)
    userRole2 = interaction.user.get_role(consultantRole.id)
    if userRole1 == None and userRole2 == None:
        await interaction.response.send_message(f"_You do not have a required role for this action._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    if not interaction.channel.name.lower().__contains__("fines"):
        await interaction.response.send_message(f"_Please use the command in the fines channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(fine.FineModal())

### FINES ###
@client.tree.command(name="my-referrals", description="Shows the list of you referrals", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    referrals = sheets.getUserReferrals(interaction.user.name)
    message = "_You don't have any referrals._"
    deleteAfter = settings.DELETE_AFTER
    if referrals != "":
        message = referrals
        deleteAfter = 300
    await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)
    
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="referrals", description="Shows the list of referrals for given user, provide discord nick", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction, username: str):
    referrals = sheets.getUserReferrals(username)
    message = "_That user doesn't have any referrals._"
    deleteAfter = settings.DELETE_AFTER
    if referrals != "":
        message = referrals
        deleteAfter = 300
    await interaction.response.send_message(f"{message}", ephemeral=True, delete_after=deleteAfter)
    
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(
    name="add-referral", 
    description="Adds the referral to employee. Please provide employee discord nick and referral discord nick.", 
    guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD]
)
async def addReferral(interaction: discord.Interaction, employee_nick: str, referral_nick: str):
    await interaction.response.defer(ephemeral=True)  # Prevents interaction expiration
    
    managementRole = util.getManagementRole(interaction)
    consultantRole = util.getConsultRole(interaction)
    
    userRole1 = interaction.user.get_role(managementRole.id)
    userRole2 = interaction.user.get_role(consultantRole.id)
    
    if userRole1 is None and userRole2 is None:
        await interaction.followup.send("_You do not have a required role for this action._", delete_after=settings.DELETE_AFTER)
        return
    
    message = "_Problem adding a referral, please check the sheets._"
    if sheets.addReferral(employee_nick, referral_nick):
        message = f"_Added {referral_nick} successfully as a referral to {employee_nick}_"
    
    await interaction.followup.send(message, delete_after=settings.DELETE_AFTER)
        
#RUN BOT
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
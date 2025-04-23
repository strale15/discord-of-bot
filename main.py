import datetime
from email.mime import message
from venv import logger
import discord
from discord.ext import commands
from discord import HTTPException, app_commands
import asyncio

import settings
from classes import massmsg, customs, formats, voice, leaks, sheets, fine, database
from util import *
import ndacheck
import util
import schedule
import os

class MyClient(commands.Bot):
    async def on_ready(self):
        log.info(f'Logged on as {self.user}!')
        
        self.scheduler = schedule.Scheduler(self, log)
        
        try:
            synced = await self.tree.sync(guild=settings.GUILD_ID)
            syncedMan = await self.tree.sync(guild=settings.M_GUILD_ID)
            syncedAnn = await self.tree.sync(guild=settings.ANNOUNCEMENT_GUILD_ID)
            syncedTrain = await self.tree.sync(guild=settings.TRAIN_GUILD_ID)
            log.info(f'Synced {len(synced)} commands, {len(syncedMan)} on management, {len(syncedTrain)} on train and {len(syncedAnn)} on announcement.')
        except Exception as e:
            log.info(f"Sync failed {e}")
            
#SETUP BOT
log = settings.logging.getLogger()
    
intents = discord.Intents.all()
intents.message_content = True

client = MyClient(command_prefix="!", intents=intents)

user_cooldowns = {}
COOLDOWN_TIME = datetime.timedelta(minutes=settings.SEND_NDA_COOLDOWN)

pdf_user_cooldowns = {}
COOLDOWN_PDF_TIME = datetime.timedelta(minutes=settings.SEND_NDA_PDF_COOLDOWN)

SIGNED_USERS_FILE = "nda/signed_users.txt"

def load_signed_users():
    try:
        with open(SIGNED_USERS_FILE, "r") as file:
            signed_users = {line.strip() for line in file.readlines()}
        return signed_users
    except FileNotFoundError:
        return set()

def save_signed_user(user_id):
    with open(SIGNED_USERS_FILE, "a") as file:
        file.write(f"{user_id}\n")
        
def check_if_already_signed(user_id):
    signed_users = load_signed_users()
    
    if str(user_id) in signed_users:
        return True
        

@client.event
async def on_member_join(member: discord.Member):
    if member.guild.id != settings.TRAIN_GUILD_ID_INT:
        return
    
    if not member.bot:
        if check_if_already_signed(member.id):
            return
        
        join_message = f"""Hello {member.global_name} and welcome to XICE.

        In this server you will go through the process of learning one of the highest degrees of OnlyFans chatting and the opportunities that lie ahead for you once you start your journey. As this is a fully remote job, this can be done anywhere in the world, so long as you have a stable internet connection and a computer that can run Infloww.

        We look forward to seeing the fullest extent of your abilities very soon!

        *Please fill in this form: https://forms.gle/jyGAT1eDR9RrktZk7*

        *Once you're done respond with 'Send NDA', I will send you the NDA to sign so you can start with the trainings*
        -#If you are unable to send messages to a bot try using discord App not the browser."""
        
        try:
            await member.send(join_message)
        except discord.Forbidden:
            log.info(f"Could not send a join DM to {member.name}")

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    if isinstance(message.channel, discord.DMChannel) and message.content.lower() == "send nda":
        user_id = message.author.id
        
        if check_if_already_signed(user_id):
            await message.channel.send(f"You have already signed the NDA.")
            return
        
        #Check google forms
        if not sheets.is_form_filled(message.author.name):
            await message.channel.send(f"Please fill in the google form. If you already did you might have inputted the wrong discord nick, please contact management.")
            return
        
        if user_id in user_cooldowns:
            last_sent_time = user_cooldowns[user_id]
            current_time = datetime.datetime.now()

            if current_time - last_sent_time < COOLDOWN_TIME:
                remaining_time = COOLDOWN_TIME - (current_time - last_sent_time)
                await message.channel.send(f"Please wait {remaining_time} before requesting the NDA again.")
                return
        
        temp_pdf = ndacheck.edit_nda_date()
        
        try:
            await message.channel.send("Please watch the guide on how to sign the NDA document and when you are done send the file to me here.")
            await message.channel.send(file=discord.File("nda/guide.mp4"))
            await message.channel.send(file=discord.File(temp_pdf))
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
        
        user_cooldowns[user_id] = datetime.datetime.now()

    if isinstance(message.channel, discord.DMChannel) and message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith(".pdf") and "XIC_NDA" in attachment.filename:
                user_id = message.author.id
        
                if check_if_already_signed(user_id):
                    await message.channel.send(f"You have already signed the NDA.")
                    return
                
                #Check google forms
                if not sheets.is_form_filled(message.author.name):
                    await message.channel.send(f"Please fill in the google form. If you already did you might have inputted the wrong discord nick, please contact management.")
                    return
        
                if user_id in pdf_user_cooldowns:
                    last_sent_time = pdf_user_cooldowns[user_id]
                    current_time = datetime.datetime.now()

                    if current_time - last_sent_time < COOLDOWN_PDF_TIME:
                        remaining_time = COOLDOWN_PDF_TIME - (current_time - last_sent_time)
                        await message.channel.send(f"Please wait {remaining_time} before sending the NDA pdf again.")
                        return
                
                date = datetime.datetime.now()
                formatted_date = date.strftime("%Y-%m-%d")
                file_path = f"./nda/{formatted_date}_{user_id}_{attachment.filename}"
                await attachment.save(file_path)
                await message.channel.send("Thanks! I received your NDA document. Checking it now...")
                pdf_user_cooldowns[user_id] = datetime.datetime.now()
                
                #Check pdf for name and signature
                check, err_msg = ndacheck.checkNda(path=file_path)
                if check:
                    #Save to drive and give role to the user
                    try:
                        ndacheck.upload_to_drive(file_path=file_path, folder_id=settings.DRIVE_FOLDER_ID)
                        save_signed_user(user_id=user_id)
                        await message.channel.send("Your NDA is all good, you will receive the trainee role shortly.")
                        
                        if await util.assign_role_by_ids(client, settings.TRAIN_GUILD_ID_INT, user_id, settings.TRAINEE_ROLE_ID):
                            await message.channel.send("You received the trainee role, you can start the training process, check the server for more info.")
                        else:
                            await message.channel.send("Something went wrong while assigning you the trainee role, please contact management.")
                    except:
                        await message.channel.send("Something went wrong while processing your NDA, please contact management.")
                else:
                    await message.channel.send(f"{err_msg}")
                
                try:
                    os.remove(file_path)
                except Exception as e:
                    log.warning(f"Error deleting file: {e}")
            break

    await client.process_commands(message)

###---------------- COMMANDS ----------------###
async def delete_message_after_delay(message: discord.Message, delay: int):
    await asyncio.sleep(delay)
    await message.delete()
            
#Global error handling        
@client.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    log.error(f"Error : {error}")
    #await interaction.response.send_message(f'Error global: ({error})', ephemeral=True, delete_after=settings.DELETE_AFTER)
       
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="ping", description="Check bot latency.", guilds=[settings.GUILD_ID])
async def testSanity(interaction: discord.Interaction):
    await interaction.response.send_message(f"*Hi!* Everything seems to work properly 😊 (everything is configured, latency - {client.latency})", ephemeral=True, delete_after=settings.DELETE_AFTER)
    
#Format command
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="format", description="Makes a nicely formatted message", guilds=[settings.GUILD_ID])
async def multiline(interaction: discord.Interaction):
    await interaction.response.send_modal(formats.FormatModal())
        
#Setup command
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="setup", description="Creates voice channel in 'clock in' based on the model category", guilds=[settings.GUILD_ID])
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
        createdChannel = await interaction.guild.create_voice_channel(settings.CROSS_EMOJI + modelName + " -", category=clockInCategory, overwrites=overwrites)
        await interaction.response.send_message(f"_Successfully created {createdChannel.name} vc!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
#Recruit command - helper
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guilds=[settings.GUILD_ID])
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
@client.tree.command(name="delete-model-info", description="Deletes all model info (categories, channels, role)", guilds=[settings.GUILD_ID])
async def executeCommand(interaction: discord.Interaction, model_name: str):
    model_name = model_name.lower()
    
    try:
        #Remove model category
        modelCategory = util.getCategoryByName(interaction.guild, model_name)
        for channel in modelCategory.channels:
            await channel.delete()
        await modelCategory.delete()
                
        #Remove model vc
        clockInCategory = getCategoryByName(interaction.guild, 'clock in')
        for channel in clockInCategory.channels:
            if channel.name.lower().__contains__(model_name):
                await channel.delete()
                break
                
        modelRole = getRoleByName(interaction.guild, model_name)
        if modelRole is not None:
            await modelRole.delete()
            
        await interaction.response.send_message(f"Successfully deleted all {model_name} info!", ephemeral=True, delete_after=settings.DELETE_AFTER)
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete model info: {e}", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
#Create role - helper
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="c-role", description="Creates role and user to it", guilds=[settings.GUILD_ID])
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=role_name, color=discord.Colour.random())
        
    await interaction.user.add_roles(modelRole)
    await interaction.response.send_message(f"You received the role {role_name}", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
@client.tree.command(
    name="ci", 
    description="Clocks you in. Use in model text channel to clock in for that model.", 
    guilds=[settings.GUILD_ID]
)
async def ciCommand(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)  # Prevents interaction expiration

    if interaction.channel.category is None:
        message = await interaction.followup.send(f"_Wrong channel, use one of the model text channels._")
        asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
        return
    
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower():
            if util.checkIfUserIsClockedIn(interaction.user, channel.name):
                message = await interaction.followup.send(f"_You are already clocked in._", ephemeral=True)
                asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
                return
            
            newChannelName = f"{channel.name}, {username}" if channel.name[-1] != '-' else f"{settings.TICK_EMOJI}{channel.name[1:]} {username}"
            await channel.edit(name=newChannelName)

            try:
                with open("clocklog.txt", "a") as file:
                    now = datetime.datetime.now()
                    datetime_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"CI [{datetime_string}] - username: {interaction.user.name} - model: {modelName}\n")
            except:
                log.warning("Error logging ci to file")

            database.insert_ping(chatter_id=interaction.user.id, model_channel_id=interaction.channel_id)
            await interaction.followup.send(f"You are now clocked in _{modelName}_.")
            return
        
    message = await interaction.followup.send(f"_Model is missing the voice channel, please create one using /setup._")
    asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
    
@ciCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking in!_", ephemeral=True, delete_after=settings.DELETE_AFTER)

@client.tree.command(
    name="co", 
    description="Clocks you out. Use in model text channel to clock out for that model.", 
    guilds=[settings.GUILD_ID]
)
async def coCommand(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)  # Prevents interaction expiration

    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower() and util.checkIfUserIsClockedIn(interaction.user, channel.name):
            # Remove username from channel name
            usernames = getClockedInUsernames(channel.name)
            usernames.remove(username)
            
            if len(usernames) == 0:
                newChannelName = settings.CROSS_EMOJI + getBaseChannelName(channel.name)[1:] + " -"
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
            
            message = await interaction.followup.send(f"You are now clocked out of _{modelName}_.", ephemeral=False)
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
            return
            
    message = await interaction.followup.send(f"_You are not clocked in on any model._", ephemeral=True)
    asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))

    
@coCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking out!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="co-all", description="Clocks everyone from vc. Use in model text channel to clock everyone out for that model.", guilds=[settings.GUILD_ID])
async def coallCommand(interaction: discord.Interaction):
    await interaction.response.send_message(f"Processing, please wait...")  # Send initial response
    
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and modelName in channel.name.lower():
            newChannelName = settings.CROSS_EMOJI + getBaseChannelName(channel.name)[1:] + " -"
            await channel.edit(name=newChannelName)
    
    message = await interaction.followup.send(f"_Everyone is now clocked out from {modelName}._", ephemeral=True)

    asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
    
@coallCommand.error
async def on_clock_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if str(error).__contains__("RateLimited"):
        await interaction.response.send_message("_Please wait at least **10** minutes before clocking everyone out!_", ephemeral=True, delete_after=settings.DELETE_AFTER)
    
### MMA ###
@client.tree.command(name="mma", description="Submit MM for approval", guilds=[settings.GUILD_ID])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-staff-chat"):
        await interaction.response.send_message(f"_Please submit mms in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(massmsg.MassMessageModal())
    
### CUSTOMS ###
@client.tree.command(name="cs", description="Submit custom for review", guilds=[settings.GUILD_ID])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-customs"):
        await interaction.response.send_message(f"_Please submit cs in customs model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(customs.CustomsModal())
    
### VOICE ###
@client.tree.command(name="voice", description="Submit voice for review", guilds=[settings.GUILD_ID])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-staff-chat"):
        await interaction.response.send_message(f"_Please submit voice in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(voice.VoiceModal())
    
### LEAKS ###
@client.tree.command(name="leaks", description="Submit a leak", guilds=[settings.GUILD_ID])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("-staff-chat"):
        await interaction.response.send_message(f"_Please submit leak in staff chat model channel._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    await interaction.response.send_modal(leaks.LeakModal())
    
### FINES ###
@client.tree.command(name="my-fines", description="Shows the list of you fines", guilds=[settings.GUILD_ID])
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
@client.tree.command(name="fines", description="Shows the list of fines for given user, provide discord nick", guilds=[settings.GUILD_ID])
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
@client.tree.command(name="fine", description="Opens a form to fine a user", guilds=[settings.GUILD_ID])
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

### REFERRALS ###
@client.tree.command(name="my-referrals", description="Shows the list of you referrals", guilds=[settings.GUILD_ID])
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
@client.tree.command(name="referrals", description="Shows the list of referrals for given user, provide discord nick", guilds=[settings.GUILD_ID])
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
    guilds=[settings.GUILD_ID]
)
async def addReferral(interaction: discord.Interaction, employee_nick: str, referral_nick: str):
    await interaction.response.defer(ephemeral=True)  # Prevents interaction expiration
    
    managementRole = util.getManagementRole(interaction)
    consultantRole = util.getConsultRole(interaction)
    
    userRole1 = interaction.user.get_role(managementRole.id)
    userRole2 = interaction.user.get_role(consultantRole.id)
    
    if userRole1 is None and userRole2 is None:
        msg = await interaction.followup.send("_You do not have a required role for this action._")
        asyncio.create_task(delete_message_after_delay(msg, settings.DELETE_AFTER))
        return
    
    message = "_Problem adding a referral, please check the sheets._"
    if sheets.addReferral(employee_nick, referral_nick):
        message = f"_Added {referral_nick} successfully as a referral to {employee_nick}_"
    
    msg = await interaction.followup.send(message)
    asyncio.create_task(delete_message_after_delay(msg, settings.DELETE_AFTER))
    
### MANAGEMENT CI/CO ###
@client.tree.command(
    name="ci", 
    description="Clocks you in",
    guilds=[settings.M_GUILD_ID]
)
async def clockIn(interaction: discord.Interaction):
    if not interaction.channel.name.__contains__("clock-in"):
        await interaction.response.send_message(f"_Please use the clock in text channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    clockInChannel = util.getUserClockInChannel(interaction.user)
    if clockInChannel is None:
        await interaction.response.send_message(f"_You do not have any management type role._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
        
    #Add user to channel name
    if util.checkIfUserIsClockedIn(interaction.user, clockInChannel.name):
        await interaction.response.send_message(f"_You are already clocked in._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    username = interaction.user.display_name
    newChannelName = f"{clockInChannel.name}, {username}" if clockInChannel.name[-1] != '-' else f"{settings.TICK_EMOJI}{clockInChannel.name[1:]} {username}"
    await clockInChannel.edit(name=newChannelName)
    
    await interaction.response.send_message(f"You are now clocked in", ephemeral=False)
    
@client.tree.command(
    name="co", 
    description="Clocks you out",
    guilds=[settings.M_GUILD_ID]
)
async def clockOut(interaction: discord.Interaction):
    if not interaction.channel.name.__contains__("clock-in"):
        await interaction.response.send_message(f"_Please use the clock in text channel_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    clockInChannel = util.getUserClockInChannel(interaction.user)
    if clockInChannel is None:
        await interaction.response.send_message(f"_You do not have any management type role._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    if not util.checkIfUserIsClockedIn(interaction.user, clockInChannel.name):
        await interaction.response.send_message(f"_You are already clocked out._", ephemeral=True, delete_after=settings.DELETE_AFTER)
        return
    
    username = interaction.user.display_name
    
    usernames = getClockedInUsernames(clockInChannel.name)
    usernames.remove(username)
    
    if len(usernames) == 0:
        newChannelName = settings.CROSS_EMOJI + getBaseChannelName(clockInChannel.name)[1:] + " -"
    else:
        newChannelName = getBaseChannelName(clockInChannel.name) + " - " + ', '.join(usernames)
        
    await clockInChannel.edit(name=newChannelName)
    
    await interaction.response.send_message(f"You are now clocked out", ephemeral=False)
        
#RUN BOT
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
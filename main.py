import settings
from util import *
import discord
from discord.ext import commands
from discord import app_commands

class MyClient(commands.Bot):
    async def on_ready(self):
        log.info(f'Logged on as {self.user}!')
        
        try:
            synced = await self.tree.sync(guild=settings.GUILD_ID)
            log.info(f'Synced {len(synced)} commands!')        
        except Exception as e:
            log.info(f"Sync failed {e}")
            
#SETUP BOT
log = settings.logging.getLogger()
    
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(command_prefix="!", intents=intents)

###---------------- COMMANDS ----------------###
            
#Global error handling        
@client.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    log.error(f"Error : {error}")
    #await interaction.response.send_message(f'Error global: ({error})', ephemeral=True)
    
@client.tree.command(name="test", description="Performs a sanity check.", guild=settings.GUILD_ID)
async def testSanity(interaction: discord.Interaction):
    await interaction.response.send_message("*Hi!* Everything seems to work properly 😊", ephemeral=True)
        
#Setup command
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="setup", description="Creates voice channel in 'clock in' based on the model category", guild=settings.GUILD_ID)
async def setupClockInChannel(interaction: discord.Interaction):
    if interaction.channel.category is None:
        await interaction.response.send_message(f"_Please use the command in appropriate model text channel._", ephemeral=True)
        return
        
    modelName = interaction.channel.category.name
    
    clockInCategory = getCategoryByName(interaction.guild, "clock in")
    if clockInCategory is None:
        await interaction.response.send_message(f"_'Clock in' category' does not exist, please create it._", ephemeral=True)
        return
    
    modelRole = getRoleByName(interaction.guild, modelName)
    if modelRole is None:
        await interaction.response.send_message(f"_{modelName} role does not exist, please create it._", ephemeral=True)
        return
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                  }
    
    try:
        createdChannel = await interaction.guild.create_voice_channel("❌" + modelName + " - ", category=clockInCategory, overwrites=overwrites)
        await interaction.response.send_message(f"_Successfully created {createdChannel.name} vc!_", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True)
        
#Recruit command - helper
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, model_name: str):
    alreadyExistingCategory = getCategoryByName(interaction.guild, model_name)
    if alreadyExistingCategory is not None:
        await interaction.response.send_message(f"_{model_name} category is already setup!_", ephemeral=True)
        return
    
    modelRole = getRoleByName(interaction.guild, model_name)
    if modelRole is None:
        await interaction.response.send_message(f"_{model_name} role does not exist, please create it._", ephemeral=True)
        return
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                }
    
    try:
        createdCategory = await interaction.guild.create_category(model_name, overwrites=overwrites)
        createdChannel = await interaction.guild.create_text_channel(model_name + " - ", category=createdCategory)
        await interaction.response.send_message(f"_Successfully created {createdChannel.name} model space!_", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True)
        
#Clean all categories command - helper
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="clean-categories", description="Cleans all categories", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    try:
        allCategories = interaction.guild.categories
        for category in allCategories:
            if category.name.lower() != "clock in":
                for channel in category.channels:
                        await channel.delete()
                await category.delete()
        await interaction.response.send_message(f"Successfully cleaned all VCs!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete category: {e}", ephemeral=True)
        
#Create role - helper
@client.tree.command(name="c-role", description="Creates role and user to it", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=role_name, color=discord.Colour.red())
        
    await interaction.user.add_roles(modelRole)
    await interaction.response.send_message(f"You received the role {role_name}", ephemeral=True)
    
#Delete role
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="d-role", description="Deletes a role", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        await interaction.response.send_message(f"_Role {role_name} does not exist!_", ephemeral=True)
        
    await modelRole.delete()
    await interaction.response.send_message(f"_{role_name} deleted!_ 🚮", ephemeral=True)
    
#Clean vcs command
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="clean-vc", description="Cleans all VCs", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    try:
        allChannels = await interaction.guild.fetch_channels()
        for channel in allChannels:
            if isinstance(channel, discord.VoiceChannel):
                await channel.delete()
        await interaction.response.send_message(f"Successfully cleaned all VCs!", ephemeral=True)
    except:
        await interaction.response.send_message(f"Failed to delete channel", ephemeral=True)
        
#Clock in command
@client.tree.command(name="ci", description="Clocks you in. Use in model text channel to clock in for that model.", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and channel.name.lower().__contains__(modelName):
            if channel.name.__contains__(username):
                await interaction.response.send_message(f"_You are already clocked in._")
                return
            
            if channel.name[-1] != '-':
                await channel.edit(name=channel.name + "+" + username)
            else:
                await channel.edit(name="✅" + channel.name[1:] + " " + username)

    
    await interaction.response.send_message(f"You are now clocked in! Good luck soldier 🫡", ephemeral=True)
    
#Clock out command
@client.tree.command(name="co", description="Clocks you out. Use in model text channel to clock out for that model.", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.name
    
    for channel in clockInCategory.channels:
        if isinstance(channel, discord.VoiceChannel) and channel.name.lower().__contains__(modelName):
            if channel.name.__contains__(username):
                #remove username from channel.name string
                usernames = getClockedInUsernames(channel.name)
                usernames.remove(username)
                
                if len(usernames) == 0:
                    newChannelName = "❌" + getBaseChannelName(channel.name)[1:] + " -"
                else:
                    newChannelName = getBaseChannelName(channel.name) + " - " + '+'.join(usernames)
                    
                await channel.edit(name=newChannelName)
                await interaction.response.send_message(f"_You are now clocked out._", ephemeral=True)
                return
            
    await interaction.response.send_message(f"_You are not clocked in on any model._", ephemeral=True)
    
### MMA ###
class ReportModal(discord.ui.Modal, title="Report User"):
    user_name = discord.ui.TextInput(label="User's Discord Name", placeholder="eg. JohnDoe#eeee", required=True, max_length=100, style=discord.TextStyle.short)
    user_id = discord.ui.TextInput(label="User's Discord ID", placeholder="To grab a user's ID, make sure Developer Mode is on.", required=True, max_length=160, style=discord.TextStyle. short)
    description = discord.ui.TextInput(label="what did they do?", placeholder="eg. Broke rule #7", required=True, min_length=200, max_length=2000, style=discord.TextStyle.paragraph)
    
    async def on_submit(self, interaction: discord. Interaction):
        await interaction.response.send_message(f"{interaction.user.mention} Thank you for submitting your report, the moderation team will see it momentarily!", ephemeral=True)
        channel = discord.utils.get(interaction.guild.channels, name=interaction.channel.name)
        await channel.send(f"Submitted by {interaction.user.mention} \n Name: {self.user_name} \n ID: {self.user_id} \n Reported For: {self.description}")
        
@client.tree.command(name="report", description="Report a user", guild=settings.GUILD_ID)
async def report(interaction: discord.Interaction):
    await interaction.response.send_modal(ReportModal())
        
#RUN BOT     
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
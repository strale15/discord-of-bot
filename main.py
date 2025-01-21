import settings
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
    log.error(f"Error type: {type(error)}")
    await interaction.response.send_message(f'Error global: ({error})')
    
@client.tree.command(name="test", description="Performs a sanity check.", guild=settings.GUILD_ID)
async def testSanity(interaction: discord.Interaction):
    await interaction.response.send_message("*Hi!* Everything seems to work properly 😊")
        
#Setup command
def getCategoryByName(guild: discord.Guild, name: str) -> discord.CategoryChannel:
    for category in guild.categories:
        if category.name.lower() == name.lower():
            return category
    return None

def getRoleByName(guild: discord.Guild, name: str) -> discord.Role:
    for role in guild.roles:
        if role.name.lower() == name.lower():
            return role
    return None

@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="setup", description="Creates voice channel in 'clock in' based on the model category", guild=settings.GUILD_ID)
async def setupClockInChannel(interaction: discord.Interaction):
    if interaction.channel.category is None:
        await interaction.response.send_message(f"_Please use the command in appropriate model text channel._")
        return
        
    modelName = interaction.channel.category.name
    
    clockInCategory = getCategoryByName(interaction.guild, "clock in")
    if clockInCategory is None:
        await interaction.response.send_message(f"_'Clock in' category' does not exist, please create it._")
        return
    
    modelRole = getRoleByName(interaction.guild, modelName)
    if modelRole is None:
        await interaction.response.send_message(f"_{modelName} role does not exist, please create it._")
        return
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                  }
    
    try:
        createdChannel = await interaction.guild.create_voice_channel("❌" + modelName + " - ", category=clockInCategory, overwrites=overwrites)
        await interaction.response.send_message(f"_Successfully created {createdChannel.name} vc!_")
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_")
        
#Recruit command - helper
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, model_name: str):
    alreadyExistingCategory = getCategoryByName(interaction.guild, model_name)
    if alreadyExistingCategory is not None:
        await interaction.response.send_message(f"_{model_name} category is already setup!_")
        return
    
    modelRole = getRoleByName(interaction.guild, model_name)
    if modelRole is None:
        await interaction.response.send_message(f"_{model_name} role does not exist, please create it._")
        return
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                  }
    
    try:
        createdCategory = await interaction.guild.create_category(model_name, overwrites=overwrites)
        createdChannel = await interaction.guild.create_text_channel(model_name + " - ", category=createdCategory)
        await interaction.response.send_message(f"_Successfully created {createdChannel.name} model space!_")
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_")
        
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
        await interaction.response.send_message(f"Successfully cleaned all VCs!")
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete category: {e}")
        
#Create role - helper
@client.tree.command(name="c-role", description="Creates role and user to it", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=role_name, color=discord.Colour.red())
        
    await interaction.user.add_roles(modelRole)
    await interaction.response.send_message(f"You received the role {role_name}")
    
#Delete role
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="d-role", description="Deletes a role", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        await interaction.response.send_message(f"_Role {role_name} does not exist!_")
        
    await modelRole.delete()
    await interaction.response.send_message(f"_{role_name} deleted!_ 🚮")
    
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
        await interaction.response.send_message(f"Successfully cleaned all VCs!")
    except:
        await interaction.response.send_message(f"Failed to delete channel")
        
#RUN BOT     
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
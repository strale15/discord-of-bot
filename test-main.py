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

    async def on_message(self, message):   
        if message.author == self.user:
            return
        #Does something when message is typed
        #await message.channel.send("message")
        #log.info(f'Message was sent: {message}')
     
#SETUP BOT
log = settings.logging.getLogger()
    
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(command_prefix="!", intents=intents)

#Global error handling        
@client.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    log.error(f"Error type: {type(error)}")
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message('You do not have a permission.')
    else:
        await interaction.response.send_message(f'Error global: ({error})')

#Commands
@client.tree.command(name="test", description="Does something", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    await interaction.response.send_message("HI!")
    
@client.tree.command(name="param", description="Does something but with param", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, number: int):
    await interaction.response.send_message(f"You entered: {number}")
    
@client.tree.command(name="raise-error", description="Raises error", guild=settings.GUILD_ID)
async def raiseErrorCommand(interaction: discord.Interaction):
    raise discord.ext.commands.CommandError("Test error")

'''
@client.tree.command(name="setup", description="Create voice channel", guild=settings.GUILD_ID)
async def createChannel(interaction: discord.Interaction, name: str):
    try:
        vc = await interaction.guild.create_voice_channel(name)
        await interaction.response.send_message(f"Successfully created {name} vc!")
    except Exception as e:
        await interaction.response.send_message(f"Channel creation failed {e}")
'''

#Delete current channel
@client.tree.command(name="delete-c", description="Deletes current VC", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    await interaction.channel.delete()

#Recruit command
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction, model_name: str):
    try:
        createdCategory = await interaction.guild.create_category(model_name)
        createdChannel = await interaction.guild.create_text_channel(model_name + " - ", category=createdCategory)
        await interaction.response.send_message(f"Successfully created {createdChannel.name} vc!")
    except Exception as e:
        await interaction.response.send_message(f"Channel creation failed {e}")
        
#Test perm command
@client.tree.command(name="test-perm", description="Tests permission", guild=settings.GUILD_ID)
@app_commands.checks.has_permissions(manage_channels=True)
#@app_commands.default_permissions(manage_channels=True)
async def executeCommandError(interaction: discord.Interaction):
    await interaction.response.send_message("You have permission!")

#Setup command
@client.tree.command(name="setup", description="Create voice channel", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    try:
        createdChannel = await interaction.guild.create_voice_channel("❌" + interaction.channel.category.name + " - ", category=interaction.channel.category)
        await interaction.response.send_message(f"Successfully created {createdChannel.name} vc!")
    except Exception as e:
        await interaction.response.send_message(f"Channel creation failed {e}")

#Clean vcs command
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
        
#Clean all categories command
@client.tree.command(name="clean-cat", description="Cleans all categories", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    try:
        allCategories = interaction.guild.categories
        for category in allCategories:
            if category.name != "TEXT CHANNELS":
                for channel in category.channels:
                        await channel.delete()
                await category.delete()
        await interaction.response.send_message(f"Successfully cleaned all VCs!")
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete category: {e}")
       

#WIP delete msg
def is_me(m):
    return m.author == client.user

@client.tree.command(name="purge-msg", description="Clean all messages in current TC", guild=settings.GUILD_ID)
async def executeCommand(interaction: discord.Interaction):
    deleted = await interaction.channel.purge(limit=100, check=is_me)
    await interaction.response.send_message(f'Deleted {len(deleted)} message(s)')
    
    
#Error handling locally
@raiseErrorCommand.error
async def raiseErrorCommand_handler(interaction: discord.Interaction, error):
    log.info(f"Error type: {type(error)}")
    await interaction.response.send_message(f'Error local: {error}')
        
   
#RUN BOT     
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
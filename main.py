import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.environ.get("TOKEN")
GUILD_ID = os.environ.get("GUILD_ID")

class MyClient(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
        try:
            synced = await self.tree.sync(guild=SERVER_ID)
            print(f'Synced {len(synced)} commands!')        
        except Exception as e:
            print(f"Sync failed {e}")

    async def on_message(self, message):   
        if message.author == self.user:
            return
        #Does something when message is typed
        #await message.channel.send("message")
        
#Bot setup
SERVER_ID = discord.Object(id=GUILD_ID)

intents = discord.Intents.all()
intents.message_content = True

client = MyClient(command_prefix="!", intents=intents)

#Commands
@client.tree.command(name="test", description="Does something", guild=SERVER_ID)
async def executeCommand(interaction: discord.Interaction):
    await interaction.response.send_message("HI!")
    
@client.tree.command(name="param", description="Does something but with param", guild=SERVER_ID)
async def executeCommand(interaction: discord.Interaction, number: int):
    await interaction.response.send_message(f"You entered: {number}")

'''
@client.tree.command(name="setup", description="Create voice channel", guild=SERVER_ID)
async def createChannel(interaction: discord.Interaction, name: str):
    try:
        vc = await interaction.guild.create_voice_channel(name)
        await interaction.response.send_message(f"Successfully created {name} vc!")
    except Exception as e:
        await interaction.response.send_message(f"Channel creation failed {e}")
'''

#Delete current channel
@client.tree.command(name="delete-c", description="Deletes current VC", guild=SERVER_ID)
async def executeCommand(interaction: discord.Interaction):
    await interaction.channel.delete()

#Recruit command
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guild=SERVER_ID)
async def executeCommand(interaction: discord.Interaction, model_name: str):
    try:
        createdCategory = await interaction.guild.create_category(model_name)
        createdChannel = await interaction.guild.create_text_channel(model_name + " - ", category=createdCategory)
        await interaction.response.send_message(f"Successfully created {createdChannel.name} vc!")
    except Exception as e:
        await interaction.response.send_message(f"Channel creation failed {e}")
        
#Test perm command
@client.tree.command(name="test-perm", description="Tests permission", guild=SERVER_ID)
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
async def executeCommandError(interaction: discord.Interaction):
    await interaction.response.send_message("You have permission!")

#Setup command
@client.tree.command(name="setup", description="Create voice channel", guild=SERVER_ID)
async def executeCommand(interaction: discord.Interaction):
    try:
        createdChannel = await interaction.guild.create_voice_channel("❌" + interaction.channel.category.name + " - ", category=interaction.channel.category)
        await interaction.response.send_message(f"Successfully created {createdChannel.name} vc!")
    except Exception as e:
        await interaction.response.send_message(f"Channel creation failed {e}")

#Clean vcs command
@client.tree.command(name="clean-vc", description="Cleans all VCs", guild=SERVER_ID)
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
@client.tree.command(name="clean-cat", description="Cleans all categories", guild=SERVER_ID)
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

@client.tree.command(name="purge-msg", description="Clean all messages in current TC", guild=SERVER_ID)
async def executeCommand(interaction: discord.Interaction):
    deleted = await interaction.channel.purge(limit=100, check=is_me)
    await interaction.response.send_message(f'Deleted {len(deleted)} message(s)')
    
    
#Error handling
@executeCommandError.error
async def info_error(interaction: discord.Interaction, error):
    print(f"Error type: {type(error)}")
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message('You do not have a permission.')
        
    
        



#Run client
client.run(BOT_TOKEN)
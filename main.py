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
    
@client.tree.command(name="test", description="Performas a sanity check.", guild=settings.GUILD_ID)
async def testSanity(interaction: discord.Interaction):
    await interaction.response.send_message("Hi! Everything seems to work properly 😊")
        
        
#RUN BOT     
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
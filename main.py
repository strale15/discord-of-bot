import discord
from discord.ext import commands
import os

import settings
import schedule

class MyClient(commands.Bot):
    async def setup_hook(self):
        log.info(f"Setting hooks up...")
        
        for cmd in self.tree.get_commands():
            log.info(f"Registered command: {cmd.name}")
        
        # Load cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                await self.load_extension(f"cogs.{filename[:-3]}")
                
    async def on_ready(self):
        log = settings.logging.getLogger()
        log.info(f'Logged in as {self.user}')
        log.info(f"Commands sync in progress...")
        
        self.scheduler = schedule.Scheduler(self, settings.logging.getLogger())
        
        try:
            syncedMain = await self.tree.sync(guild=settings.GUILD_ID)
            syncedMan = await self.tree.sync(guild=settings.M_GUILD_ID)
            syncedAnn = await self.tree.sync(guild=settings.ANNOUNCEMENT_GUILD_ID)
            syncedTrain = await self.tree.sync(guild=settings.TRAIN_GUILD_ID)
            log.info(f'Synced commands: {len(syncedMain)} on main, {len(syncedMan)} on management, {len(syncedTrain)} on train and {len(syncedAnn)} on announcement.')
        except Exception as e:
            log.info(f"Sync failed {e}")

# Setup bot
log = settings.logging.getLogger()
intents = discord.Intents.all()
intents.message_content = True

client = MyClient(command_prefix="!", intents=intents)

@client.tree.error
async def on_error(interaction, error):
    log.error(f"Error: {error}")

if __name__ == "__main__":
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
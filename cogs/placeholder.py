import discord
from discord.ext import commands
from discord import app_commands, Interaction

import settings
from util import *

class Placeholder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def cog_load(self):
        self.bot.tree.add_command(self.ping, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(Placeholder(bot))
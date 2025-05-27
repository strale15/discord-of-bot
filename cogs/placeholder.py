from discord.ext import commands
from discord import app_commands, Interaction
import settings

class Placeholder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Placeholder(bot))
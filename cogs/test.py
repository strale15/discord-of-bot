from discord.ext import commands
from discord import app_commands, Interaction
import settings

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message(f"Hi! Latency: {self.bot.latency}", ephemeral=True)
        
    async def cog_load(self):
        self.bot.tree.add_command(self.ping, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(Misc(bot))
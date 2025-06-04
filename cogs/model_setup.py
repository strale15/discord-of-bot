import discord
from discord.ext import commands
from discord import app_commands

from util import *
import settings

class ModelSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    #Setup command
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(name="setup", description="Creates voice channel in 'clock in' based on the model category")
    async def setupClockInChannel(self, interaction: discord.Interaction):
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
        
        supervisorRole = getSupervisorRole(interaction)
        
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
    @app_commands.command(name="recruit", description="Create basic category and channel for a model")
    async def recruit(self, interaction: discord.Interaction, model_name: str):
        await interaction.response.defer(ephemeral=True)
        
        alreadyExistingCategory = getCategoryByName(interaction.guild, model_name)
        if alreadyExistingCategory is not None:
            message = await interaction.followup.send(f"_{model_name} category is already setup!_")
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
            return
        
        roleName = f"Team {model_name}"
        modelRole = getRoleByName(interaction.guild, roleName)
        if modelRole is None:
            modelRole = await interaction.guild.create_role(name=roleName, color=discord.Colour.magenta())
            
        ppvRole = getPPVEngRole(interaction)
        supervisorRole = getSupervisorRole(interaction)
        
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
            
            #Update chatter announcement channel permissions
            announcement_channel = interaction.guild.get_channel(settings.CHATTER_ANNOUNCEMENT_CHANNEL_ID)
            announcement_overwrites = announcement_channel.overwrites
            announcement_overwrites[modelRole] = discord.PermissionOverwrite(view_channel=True, read_messages=True)
            await announcement_channel.edit(overwrites=announcement_overwrites)
            
            message = await interaction.followup.send(f"_Successfully created {model_name} model space, you can now use /setup in staff chat to create clock in vc!_")
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
        except Exception as e:
            message = await interaction.followup.send(f"_Channel creation failed {e}_")
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
            
    #Clean model info
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.command(name="delete-model-info", description="Deletes all model info (categories, channels, role)")
    async def deleteModelInfo(self, interaction: discord.Interaction, model_name: str):
        await interaction.response.defer(ephemeral=True)
        model_name = model_name.lower()
        
        try:
            modelRole = getRoleByName(interaction.guild, model_name)
            if modelRole is not None:
                await modelRole.delete()
                
            #Remove model category
            modelCategory = getCategoryByName(interaction.guild, model_name)
            for channel in modelCategory.channels:
                await channel.delete()
            await modelCategory.delete()
                    
            #Remove model vc
            clockInCategory = getCategoryByName(interaction.guild, 'clock in')
            for channel in clockInCategory.channels:
                if channel.name.lower().__contains__(model_name):
                    await channel.delete()
                    break
                    
            try:
                message = await interaction.followup.send(f"Successfully deleted all {model_name} info!")
                asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
            except discord.errors.NotFound:
                pass
            
        except Exception as e:
            try:
                message = await interaction.followup.send(f"Failed to delete model info: {e}")
                asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
            except discord.errors.NotFound:
                pass
            
    async def cog_load(self):
        self.bot.tree.add_command(self.setupClockInChannel, guild=settings.GUILD_ID)
        self.bot.tree.add_command(self.recruit, guild=settings.GUILD_ID)
        self.bot.tree.add_command(self.deleteModelInfo, guild=settings.GUILD_ID)

async def setup(bot):
    await bot.add_cog(ModelSetupCog(bot))
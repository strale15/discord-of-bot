from multiprocessing.dummy import Value
from urllib import request
import settings
from util import *
import discord
from discord.ext import commands
from discord import app_commands

import util

class MyClient(commands.Bot):
    async def on_ready(self):
        log.info(f'Logged on as {self.user}!')
        
        try:
            syncedDev = await self.tree.sync(guild=settings.GUILD_ID_DEV)
            syncedProd = await self.tree.sync(guild=settings.GUILD_ID_PROD)
            log.info(f'Synced {len(syncedDev)} on dev and {len(syncedProd)} commands on prod!')        
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
    
@client.tree.command(name="test", description="Performs a sanity check.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def testSanity(interaction: discord.Interaction):
    await interaction.response.send_message("*Hi!* Everything seems to work properly 😊", ephemeral=True)
        
#Setup command
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="setup", description="Creates voice channel in 'clock in' based on the model category", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def setupClockInChannel(interaction: discord.Interaction):
    if interaction.channel.category is None:
        await interaction.response.send_message(f"_Please use the command in appropriate model text channel._", ephemeral=True)
        return
        
    modelName = interaction.channel.category.name
    
    clockInCategory = getCategoryByName(interaction.guild, "clock in")
    if clockInCategory is None:
        await interaction.response.send_message(f"_'Clock in' category' does not exist, please create it._", ephemeral=True)
        return
    
    for voice in clockInCategory.voice_channels:
        if voice.name.lower().__contains__(modelName.lower()):
            await interaction.response.send_message(f"_Model voice channel is already setup._", ephemeral=True)
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
@client.tree.command(name="recruit", description="Create basic category and channel for a model", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, model_name: str):
    alreadyExistingCategory = getCategoryByName(interaction.guild, model_name)
    if alreadyExistingCategory is not None:
        await interaction.response.send_message(f"_{model_name} category is already setup!_", ephemeral=True)
        return
    
    modelRole = getRoleByName(interaction.guild, model_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=model_name, color=discord.Colour.red())
    
    overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False),
                    modelRole: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
                }
    
    try:
        createdCategory = await interaction.guild.create_category(model_name, overwrites=overwrites)
        await interaction.guild.create_text_channel("💬-staff-chat", category=createdCategory)
        await interaction.guild.create_text_channel("📰-info", category=createdCategory)
        await interaction.guild.create_text_channel("📨-mma-request", category=createdCategory)
        await interaction.guild.create_text_channel("📷-cs-request", category=createdCategory)
        await interaction.response.send_message(f"_Successfully created {model_name} model space!_", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"_Channel creation failed {e}_", ephemeral=True)
        
#Clean model info
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.default_permissions(manage_channels=True)
@client.tree.command(name="delete-model-info", description="Deletes all model info (categories, channels, role)", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, model_name: str):
    model_name = model_name.lower()
    
    try:
        #Remove model category
        allCategories = interaction.guild.categories
        for category in allCategories:
            if category.name.lower().__contains__(model_name):
                for channel in category.channels:
                        await channel.delete()
                await category.delete()
                
        #Remove model vc
        allChannels = interaction.guild.channels
        for channel in allChannels:
            if channel.name.lower().__contains__(model_name):
                await channel.delete()
                
        modelRole = getRoleByName(interaction.guild, model_name)
        if modelRole is not None:
            await modelRole.delete()
            
        await interaction.response.send_message(f"Successfully deleted all {model_name} info!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete model info: {e}", ephemeral=True)
        
#Create role - helper
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="c-role", description="Creates role and user to it", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        modelRole = await interaction.guild.create_role(name=role_name, color=discord.Colour.random())
        
    await interaction.user.add_roles(modelRole)
    await interaction.response.send_message(f"You received the role {role_name}", ephemeral=True)
    
#Delete role
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.default_permissions(manage_roles=True)
@client.tree.command(name="d-role", description="Deletes a role", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction, role_name: str):
    modelRole = getRoleByName(interaction.guild, role_name)
    if modelRole is None:
        await interaction.response.send_message(f"_Role {role_name} does not exist!_", ephemeral=True)
        
    await modelRole.delete()
    await interaction.response.send_message(f"_{role_name} deleted!_ 🚮", ephemeral=True)
        
#Clock in command
@client.tree.command(name="ci", description="Clocks you in. Use in model text channel to clock in for that model.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction):
    if interaction.channel.category is None:
        await interaction.response.send_message(f"_Wrong channel, use one of the model text channels._")
        return
    
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
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
            return
        
    await interaction.response.send_message(f"_Model is missing the voice channel, please create one using /setup._", ephemeral=True)
    
#Clock out command
@client.tree.command(name="co", description="Clocks you out. Use in model text channel to clock out for that model.", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def executeCommand(interaction: discord.Interaction):
    modelName = interaction.channel.category.name.lower()
    clockInCategory = getCategoryByName(interaction.guild, 'clock in')
    username = interaction.user.display_name
    
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
class MassMessageChangeModal(discord.ui.Modal, title="Comment on MM"):
    def __init__(self, ctx: discord.Interaction, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, requestMsg: discord.Message, embed: discord.Embed):
        super().__init__(title="Request change for mm") 
        self.ctx = ctx
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName =  modelName
        self.requestMsg = requestMsg
        self.embed = embed
           
        self.comment = discord.ui.TextInput(
            label="Comment:",
            placeholder="You comment...",
            required=True,
            min_length=1,
            max_length=1000,
            style=discord.TextStyle.paragraph,
        )
        
        self.proposition = discord.ui.TextInput(
            label="Edited MM:",
            placeholder="Your edited mm...",
            required=False,
            default=embed.fields[0].value,
            min_length=0,
            max_length=1000,
            style=discord.TextStyle.paragraph,
        )

        # Add the field to the modal
        self.add_item(self.comment)
        self.add_item(self.proposition)
    
    async def on_submit(self, interaction: discord. Interaction):
        await self.requestMsg.delete()
        
        self.embed.color = discord.Color.yellow()
        self.embed.remove_footer()
        self.embed.fields[0].name = "Original mm"
        self.embed.fields[0].inline = False
        self.embed.add_field(name="Comment", value=self.comment.value, inline=False)
        if len(self.proposition.value) > 0 and self.proposition.value != self.embed.fields[0].value:
            self.embed.add_field(name="Proposed change:", value=self.proposition.value, inline=False)
        
        
        await self.requestChannel.send(f"{self.employee.mention} your mm for **{self.modelName}** request change by **{interaction.user.display_name}**\n_Commented mm:_", embed=self.embed)
        await interaction.response.send_message(f"_Change requested_", ephemeral=True)

class MmaView(discord.ui.View):
    def __init__(self, mm: discord.Message, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, embed: discord.Embed):
        super().__init__(timeout=None)
        
        self.mm = mm
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName = modelName
        self.embed = embed

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.mm.delete()
        self.embed.color = discord.Color.green()
        self.embed.remove_footer()
        await self.requestChannel.send(f"{self.employee.mention} your mm for **{self.modelName}** was approved by **{interaction.user.display_name}**\n_Approved mm request:_", embed=self.embed)
        await interaction.response.send_message(f"_Approved the mm_", ephemeral=True)
        
    @discord.ui.button(label="Request change", style=discord.ButtonStyle.blurple)
    async def requestChange(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_modal(MassMessageChangeModal(interaction, self.requestChannel, self.employee, self.modelName, self.mm, self.embed))
        
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.mm.delete()
        try:
            self.embed.color = discord.Color.red()
            self.embed.remove_footer()
            await self.requestChannel.send(f"{self.employee.mention} your mm for **{self.modelName}** was rejected by **{interaction.user.display_name}**\n_Rejected mm request:_", embed=self.embed)
            await interaction.response.send_message(f"_Rejected the mm_", ephemeral=True)
        except:
            await interaction.response.send_message(f"_Rejected the mm but there was an error with sending the notification._", ephemeral=True)

class MassMessageModal(discord.ui.Modal, title="Submit MM"):
    def __init__(self):
        super().__init__(title="Submit MM")    
        self.mass_message = discord.ui.TextInput(
            label="Mass message:",
            placeholder="Message...",
            required=True,
            min_length=1,
            max_length=1000,
            style=discord.TextStyle.paragraph,
        )

        # Add the field to the modal
        self.add_item(self.mass_message)

    
    async def on_submit(self, interaction: discord. Interaction):
        try:
            #Send mm for review
            channel = util.getMmaApprovalChannel(interaction)
            
            embed_message = discord.Embed(title=interaction.channel.category.name + " - MM", color=discord.Color.blue())
            embed_message.set_author(name=f"Requested by {interaction.user.display_name} ({interaction.user})", icon_url=interaction.user.avatar)
            embed_message.add_field(name="Message", value=self.mass_message.value, inline=True)
            embed_message.set_footer(text="Review decision:")
            
            thumbnail_path = "res/envelope.png"
            thumbnail_filename = "envelope.png"
            embed_message.set_thumbnail(url=f"attachment://{thumbnail_filename}")

            with open(thumbnail_path, "rb") as file:
                message = await channel.send(
                    content=f"{interaction.user.mention} submitted a mass message for review:",
                    embed=embed_message,
                    file=discord.File(file, filename=thumbnail_filename)
                )
                await message.edit(view=MmaView(message, interaction.channel, interaction.user, interaction.channel.category.name, embed_message))

            await interaction.response.send_message(f"{interaction.user.mention} Thank you for submitting your mm, it will be reviewed!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"_Error submitting the mm, contact staff {e}_", ephemeral=True)
        
@client.tree.command(name="mma", description="Submit MM for approval", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("mma-request"):
        await interaction.response.send_message(f"_Please submit mms in mma request channel._", ephemeral=True)
        return
    await interaction.response.send_modal(MassMessageModal())
    
### CUSTOMS ###
class CsView(discord.ui.View):
    def __init__(self, mm: discord.Message, requestChannel: discord.TextChannel, user: discord.User, modelName: str, embed: discord.Embed):
        super().__init__(timeout=None)
        
        self.mm = mm
        self.requestChannel = requestChannel
        self.user = user
        self.modelName = modelName
        self.embed = embed

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.mm.delete()
        self.embed.color = discord.Color.green()
        await self.requestChannel.send(f"{self.user.mention} your cs for **{self.modelName}** was approved by **{interaction.user.display_name}**\n_Custom:_", embed=self.embed)
        await interaction.response.send_message(f"_Approved the cs_", ephemeral=True)
        
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.mm.delete()
        self.embed.color = discord.Color.red()
        await self.requestChannel.send(f"{self.user.mention} your cs for **{self.modelName}** was rejected by **{interaction.user.display_name}**\n_Custom:_", embed=self.embed)
        await interaction.response.send_message(f"_Rejected the cs_", ephemeral=True)

class CustomsModal(discord.ui.Modal, title="Submit Custom"):
    def __init__(self):
        super().__init__(title="Submit Custom")    
        self.ofName = discord.ui.TextInput(
            label="Onlyfans username:",
            placeholder="some incel username",
            required=True,
            min_length=1,
            max_length=20,
            style=discord.TextStyle.short,
        )
        
        self.date = discord.ui.TextInput(
            label="Date:",
            placeholder="10/01/2025",
            required=True,
            min_length=1,
            max_length=20,
            style=discord.TextStyle.short,
        )
        
        self.paid = discord.ui.TextInput(
            label="$ Paid (Lifetime):",
            placeholder="500",
            required=True,
            min_length=1,
            max_length=20,
            style=discord.TextStyle.short,
        )
        
        self.details = discord.ui.TextInput(
            label="Details:",
            placeholder="details...",
            required=True,
            min_length=1,
            max_length=500,
            style=discord.TextStyle.paragraph,
        )
        
        # Add the field to the modal
        self.add_item(self.ofName)
        self.add_item(self.date)
        self.add_item(self.paid)
        self.add_item(self.details)

    
    async def on_submit(self, interaction: discord. Interaction):
        try:
            #Send custom for review
            channel = util.getCsApprovalChannel(interaction)
            
            embed_message = discord.Embed(title=interaction.channel.category.name + " - Custom", color=discord.Color.green())
            embed_message.set_author(name=f"Requested by {interaction.user.display_name} ({interaction.user})", icon_url=interaction.user.avatar)
            embed_message.add_field(name="OF Name:", value=self.ofName.value, inline=True)
            embed_message.add_field(name="Date:", value=self.date.value, inline=True)
            embed_message.add_field(name="$ Paid (Lifetime):", value=self.paid.value, inline=True)
            embed_message.add_field(name="Details:", value=self.details.value, inline=True)
            embed_message.set_footer(text="Review decision:")
            
            thumbnail_path = "res/request.png"
            thumbnail_filename = "request.png"
            embed_message.set_thumbnail(url=f"attachment://{thumbnail_filename}")

            with open(thumbnail_path, "rb") as file:
                message = await channel.send(
                    content=f"{interaction.user.mention} submitted a custom for review:",
                    embed=embed_message,
                    file=discord.File(file, filename=thumbnail_filename)
                )
                await message.edit(view=CsView(message, interaction.channel, interaction.user, interaction.channel.category.name, embed_message))

            await interaction.response.send_message(f"{interaction.user.mention} Thank you for submitting your custom, it will be reviewed!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"_Error submitting the custom, contact staff {e}_", ephemeral=True)
        
        
@client.tree.command(name="cs", description="Submit custom for approval", guilds=[settings.GUILD_ID_DEV, settings.GUILD_ID_PROD])
async def report(interaction: discord.Interaction):
    if not interaction.channel.name.lower().__contains__("cs-request"):
        await interaction.response.send_message(f"_Please submit cs in cs request channel._", ephemeral=True)
        return
    await interaction.response.send_modal(CustomsModal())

        
#RUN BOT     
if __name__ == "__main__":
    #Run client
    client.run(settings.DISCORD_API_SECRET, root_logger=True)
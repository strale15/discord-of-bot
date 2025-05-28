from ast import Str
import asyncio
from os import name
import util
import discord
import settings
import schedule
from datetime import datetime as dt
import threading
from classes import database
from util import delete_message_after_delay

lock = threading.Lock()

def remove_mm_from_queue(message: discord.Message):
    with lock:
        schedule.mm_time_queue.remove_by_key(message.id)

#COMMENT MMA MODAL
class MassMessageCommentModal(discord.ui.Modal, title="Comment on MM"):
    def __init__(self, ctx: discord.Interaction, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, requestMsg: discord.Message, embed: discord.Embed, mmConfirmationMsg: discord.Message):
        super().__init__(title="Comment on MM") 
        self.ctx = ctx
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName =  modelName
        self.requestMsg = requestMsg
        self.embed = embed
        self.mmConfirmationMsg = mmConfirmationMsg
           
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
        mmText = self.embed.fields[0].value
        
        remove_mm_from_queue(self.requestMsg)
        await self.requestMsg.delete()
        
        self.embed.color = discord.Color.yellow()
        self.embed.remove_footer()
        self.embed.set_field_at(0, name="Original message", value=self.embed.fields[0].value, inline=False)
        self.embed.add_field(name="Comment", value=self.comment.value, inline=False)
        if len(self.proposition.value) > 0 and self.proposition.value != self.embed.fields[0].value:
            self.embed.add_field(name="Proposed change:", value=self.proposition.value, inline=False)
            mmText = self.proposition.value
        
        message = await self.requestChannel.send(f"{self.employee.mention} your mm for **{self.modelName}** request change by **{interaction.user.display_name}**\n_Commented mm:_", embed=self.embed)
        await message.edit(view=FixMmaView(message, interaction.channel, self.employee, interaction.channel.category.name, mmText))
        
        await util.delete_message_ignore_exception(self.mmConfirmationMsg, source="MMA Comment")
        await interaction.response.send_message(f"_Change requested_", ephemeral=True, delete_after=settings.DELETE_AFTER)

#APPROVE COMMENT MMA MODAL
class MassMessageApproveAndCommentModal(discord.ui.Modal, title="Approve and comment on MM"):
    def __init__(self, ctx: discord.Interaction, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, requestMsg: discord.Message, embed: discord.Embed, mmConfirmationMsg: discord.Message):
        super().__init__(title="Approve and comment on MM") 
        self.ctx = ctx
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName =  modelName
        self.requestMsg = requestMsg
        self.embed = embed
        self.mmConfirmationMsg = mmConfirmationMsg
           
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
        originalMessage = self.embed.fields[0].value
        
        remove_mm_from_queue(self.requestMsg)
        await self.requestMsg.delete()
        
        self.embed.color = discord.Color.green()
        self.embed.remove_footer()
        self.embed.remove_field(0)
        
        self.embed.add_field(name="Comment", value=self.comment.value, inline=False)
        if len(self.proposition.value) > 0 and self.proposition.value != self.embed.fields[0].value:
            originalMessage = self.proposition.value
        
        
        await self.requestChannel.send(f"{self.employee.mention} your mm for **{self.modelName}** was approved and commented by **{interaction.user.display_name}**\n**Message for clipboard:**\n{settings.LINE_TEXT}\n{originalMessage}\n{settings.LINE_TEXT}\n", embed=self.embed)
        await util.delete_message_ignore_exception(self.mmConfirmationMsg, source="MMA Approve and comment")
        await interaction.response.send_message(f"_Approved the mm with comment_", ephemeral=True, delete_after=settings.DELETE_AFTER)

#BUTTON FOR MMA REQUEST (approve, approve with comment, comment, reject)
class MmaView(discord.ui.View):
    def __init__(self, mm: discord.Message, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, embed: discord.Embed, mmConfirmationMsg: discord.Message):
        super().__init__(timeout=None)
        
        self.mm = mm
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName = modelName
        self.embed = embed
        self.mmConfirmationMsg = mmConfirmationMsg

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, Button: discord.ui.Button):
        originalMessage = self.embed.fields[0].value
        
        remove_mm_from_queue(self.mm)
        await self.mm.delete()
        
        self.embed.set_field_at(0, name="APPROVED", value="", inline=False)
        self.embed.color = discord.Color.green()
        self.embed.remove_footer()
        
        await self.requestChannel.send(
            f"{self.employee.mention} your mm for **{self.modelName}** was approved by **{interaction.user.display_name}**\n**Message for clipboard:**\n{settings.LINE_TEXT}\n{originalMessage}\n{settings.LINE_TEXT}\n",
            embed=self.embed
        )
        await util.delete_message_ignore_exception(self.mmConfirmationMsg, source="MMA Approve")
        await interaction.response.send_message(f"_Approved the mm_", ephemeral=True, delete_after=settings.DELETE_AFTER)

        
    @discord.ui.button(label="Approve with comment", style=discord.ButtonStyle.green)
    async def approveAndComment(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_modal(MassMessageApproveAndCommentModal(interaction, self.requestChannel, self.employee, self.modelName, self.mm, self.embed, self.mmConfirmationMsg))
        
    @discord.ui.button(label="Comment", style=discord.ButtonStyle.blurple)
    async def requestChange(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_modal(MassMessageCommentModal(interaction, self.requestChannel, self.employee, self.modelName, self.mm, self.embed, self.mmConfirmationMsg))
        
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, Button: discord.ui.Button):
        remove_mm_from_queue(self.mm)
        await self.mm.delete()
        try:
            self.embed.color = discord.Color.red()
            self.embed.remove_footer()
            await self.requestChannel.send(f"{self.employee.mention} your mm for **{self.modelName}** was rejected by **{interaction.user.display_name}**\n_Rejected mm request:_", embed=self.embed)
            
            await util.delete_message_ignore_exception(self.mmConfirmationMsg, source="MMA Reject")
            await interaction.response.send_message(f"_Rejected the mm_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        except:
            await interaction.response.send_message(f"_Rejected the mm but there was an error with sending the notification._", ephemeral=True, delete_after=settings.DELETE_AFTER)

#'FIX ME' BUTTON ON COMMENTED MM (so chatters can fix them without typing /mma)     
class FixMmaView(discord.ui.View):
    def __init__(self, mm: discord.Message, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, message: str):
        super().__init__(timeout=None)
        
        self.mm = mm
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName = modelName
        self.message = message

    @discord.ui.button(label="Fix me", style=discord.ButtonStyle.green)
    async def fixMma(self, interaction: discord.Interaction, Button: discord.ui.Button):
        if(interaction.user.id == self.employee.id):     
            await interaction.response.send_modal(MassMessageModal(message=self.message, commentedMMEmbed=self.mm))
        else:
            await interaction.response.send_message(f"_This is not your mm._", ephemeral=True, delete_after=settings.DELETE_AFTER)

#MODAL THAT CHATTERS USE TO SUBMIT MM FOR REVIEW
class MassMessageModal(discord.ui.Modal, title="Submit MM"):
    def __init__(self, message: str = "", commentedMMEmbed: discord.Message=None):
        super().__init__(title="Submit MM")
        
        self.commentedMMEmbed = commentedMMEmbed
        
        self.mass_message = discord.ui.TextInput(
            label="Mass message:",
            placeholder="Message...",
            required=True,
            min_length=1,
            max_length=1000,
            style=discord.TextStyle.paragraph,
            default=message  # Set default value if provided
        )

        # Add the field to the modal
        self.add_item(self.mass_message)

    
    async def on_submit(self, interaction: discord. Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            #Send mm for review
            channel = util.getMmaApprovalChannel(interaction)
            
            embed_message = discord.Embed(title=interaction.channel.category.name + " - MM", color=discord.Color.blue())
            embed_message.set_author(name=f"Requested by {interaction.user.display_name} ({interaction.user})", icon_url=interaction.user.avatar)
            embed_message.add_field(name="Message", value=self.mass_message.value, inline=True)
            embed_message.set_footer(text="Review decision:")
            
            thumbnail_path = "resources/icons/envelope.png"
            thumbnail_filename = "envelope.png"
            embed_message.set_thumbnail(url=f"attachment://{thumbnail_filename}")
            
            mmConfirmationMsg = await interaction.followup.send(f"_Processing your mm..._")

            with open(thumbnail_path, "rb") as file:
                message = await channel.send(
                    content=f"{interaction.user.mention} submitted a mass message for review:",
                    embed=embed_message,
                    file=discord.File(file, filename=thumbnail_filename)
                )
                await message.edit(view=MmaView(message, interaction.channel, interaction.user, interaction.channel.category.name, embed_message, mmConfirmationMsg))
 
            if self.commentedMMEmbed != None:
                await self.commentedMMEmbed.edit(view=None)
                
            #Push mm to ping queue
            with lock:
                schedule.mm_time_queue.add(message.id, dt.now())
            
            database.delete_ping(chatter_id=interaction.user.id, model_channel_id=interaction.channel_id)
            
            #If user is not clocked in add grace period for mma pinging
            if not util.checkIfUserIsClockedInByIds(interaction=interaction, user_id=interaction.user.id, model_channel_id=interaction.channel_id):
                database.insert_mma_sent(user_id=interaction.user.id, model_channel_id=interaction.channel_id)
                
            await mmConfirmationMsg.edit(content=f"{interaction.user.mention} Thank you for submitting your mm, it will be reviewed!")
            asyncio.create_task(delete_message_after_delay(mmConfirmationMsg, settings.DELETE_SUBMITTED_MM_AFTER))
        except Exception as e:
            message = await interaction.followup.send(f"_Error submitting the mm, contact staff {e}_")
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
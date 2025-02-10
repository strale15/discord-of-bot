import util
import discord
import settings
     
class VoiceView(discord.ui.View):
    def __init__(self, leakMessage: discord.Message, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, embed: discord.Embed):
        super().__init__(timeout=None)
        
        self.leakMessage = leakMessage
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName = modelName
        self.embed = embed
        
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.leakMessage.delete()
        self.embed.color = discord.Color.dark_green()
        self.embed.remove_footer()
        await self.requestChannel.send(f"{self.employee.mention} your voice request for **{self.modelName}** was approved by **{interaction.user.display_name}**, it will be added to the vault.\n_Approved voice request:_", embed=self.embed)
        await interaction.response.send_message(f"_Approved a voice request_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.leakMessage.delete()
        try:
            self.embed.color = discord.Color.dark_red()
            self.embed.remove_footer()
            await self.requestChannel.send(f"{self.employee.mention} your voice request for **{self.modelName}** was rejected by **{interaction.user.display_name}**\n_Rejected voice request request:_", embed=self.embed)
            await interaction.response.send_message(f"_Rejected a voice request_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        except:
            await interaction.response.send_message(f"_Rejected the mm but there was an error with sending the notification._", ephemeral=True, delete_after=settings.DELETE_AFTER)

class VoiceModal(discord.ui.Modal, title="Submit voice request"):
    def __init__(self):
        super().__init__(title="Submit voice request")    

        self.voiceMsg = discord.ui.TextInput(
            label="Voice message:",
            placeholder= "Good boy *fart sound*...",
            required=True,
            min_length=1,
            max_length=500,
            style=discord.TextStyle.paragraph,
        )
        
        self.details = discord.ui.TextInput(
            label="Additional details:",
            placeholder="details...",
            required=False,
            min_length=0,
            max_length=500,
            style=discord.TextStyle.paragraph,
        )
        
        # Add the field to the modal
        self.add_item(self.voiceMsg)
        self.add_item(self.details)

    
    async def on_submit(self, interaction: discord. Interaction):
        try:
            #Send voice in queue
            channel = util.getVoiceQueueChannel(interaction)
            
            embed_message = discord.Embed(title=interaction.channel.category.name + " - Voice", color=discord.Color.dark_purple())
            embed_message.set_author(name=f"Requested by {interaction.user.display_name} ({interaction.user})", icon_url=interaction.user.avatar)
            embed_message.add_field(name="Voice:", value=self.voiceMsg.value, inline=False)
            if self.details.value != "":
                embed_message.add_field(name="Details:", value=self.details.value, inline=False)
            embed_message.set_footer(text="Decision:")
            
            thumbnail_path = "res/speaker.png"
            thumbnail_filename = "speaker.png"
            embed_message.set_thumbnail(url=f"attachment://{thumbnail_filename}")

            with open(thumbnail_path, "rb") as file:
                message = await channel.send(
                    content=f"{interaction.user.mention} submitted a voice request:",
                    embed=embed_message,
                    file=discord.File(file, filename=thumbnail_filename)
                )
                await message.edit(view=VoiceView(message, interaction.channel, interaction.user, interaction.channel.category.name, embed_message))

            await interaction.response.send_message(f"{interaction.user.mention} Thank you for submitting a voice request, it will be reviewed!", ephemeral=True, delete_after=settings.DELETE_AFTER)
        except Exception as e:
            await interaction.response.send_message(f"_Error submitting a voice request, contact staff {e}_", ephemeral=True, delete_after=settings.DELETE_AFTER)
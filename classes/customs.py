import util
import discord
import settings

class CustomsChangeModal(discord.ui.Modal, title="Comment on CS"):
    def __init__(self, ctx: discord.Interaction, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, requestMsg: discord.Message, embed: discord.Embed):
        super().__init__(title="Request change for cs") 
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

        # Add the field to the modal
        self.add_item(self.comment)
    
    async def on_submit(self, interaction: discord. Interaction):
        await self.requestMsg.delete()
        
        self.embed.color = discord.Color.dark_blue()
        self.embed.remove_footer()
        self.embed.add_field(name="Comment", value=self.comment.value, inline=False)
        
        await self.requestChannel.send(f"{self.employee.mention} your cs for **{self.modelName}** is commented by **{interaction.user.display_name}**\n_Commented cs:_", embed=self.embed)
        await interaction.response.send_message(f"_Change requested_", ephemeral=True, delete_after=settings.DELETE_AFTER)
        
class CsView(discord.ui.View):
    def __init__(self, cs: discord.Message, requestChannel: discord.TextChannel, employee: discord.User, modelName: str, embed: discord.Embed):
        super().__init__(timeout=None)
        
        self.cs = cs
        self.requestChannel = requestChannel
        self.employee = employee
        self.modelName = modelName
        self.embed = embed
        
    @discord.ui.button(label="Add comment", style=discord.ButtonStyle.blurple)
    async def requestChange(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_modal(CustomsChangeModal(interaction, self.requestChannel, self.employee, self.modelName, self.cs, self.embed))

class CustomsModal(discord.ui.Modal, title="Submit Custom"):
    def __init__(self):
        super().__init__(title="Submit Custom")    
        self.ofName = discord.ui.TextInput(
            label="Onlyfans username:",
            placeholder="some username...",
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
                consultantRole = util.getConsultRole(interaction)
                message = await channel.send(
                    content=f"{consultantRole.mention}\n{interaction.user.mention} submitted a custom for review:",
                    embed=embed_message,
                    file=discord.File(file, filename=thumbnail_filename)
                )
                await message.edit(view=CsView(message, interaction.channel, interaction.user, interaction.channel.category.name, embed_message))

            await interaction.response.send_message(f"{interaction.user.mention} Thank you for submitting your custom, it will be reviewed!", ephemeral=True, delete_after=settings.DELETE_AFTER)
        except Exception as e:
            await interaction.response.send_message(f"_Error submitting the custom, contact staff {e}_", ephemeral=True, delete_after=settings.DELETE_AFTER)
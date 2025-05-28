import util
import discord
import settings
     
class LeaksView(discord.ui.View):
    def __init__(self, leakMessage: discord.Message):
        super().__init__(timeout=None)
        
        self.leakMessage = leakMessage
        
    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def requestChange(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.leakMessage.delete()
        await interaction.response.send_message(f"_Removed from queue_", ephemeral=True, delete_after=settings.DELETE_AFTER)

class LeakModal(discord.ui.Modal, title="Submit a leak"):
    def __init__(self):
        super().__init__(title="Submit a leak")    

        self.leakLinks = discord.ui.TextInput(
            label="Leak links:",
            placeholder= "https://youtu.be/j8tKkkP9LIg",
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
        self.add_item(self.leakLinks)
        self.add_item(self.details)

    
    async def on_submit(self, interaction: discord. Interaction):
        try:
            #Send voice in queue
            channel = util.getLeaksChannel(interaction)
            
            embed_message = discord.Embed(title=interaction.channel.category.name + " - Leak", color=discord.Color.blue())
            embed_message.set_author(name=f"Leak found by {interaction.user.display_name} ({interaction.user})", icon_url=interaction.user.avatar)
            embed_message.add_field(name="Links:", value=self.leakLinks.value, inline=False)
            if self.details.value != "":
                embed_message.add_field(name="Details:", value=self.details.value, inline=False)
            embed_message.set_footer(text="Resolve:")
            
            thumbnail_path = "resources/icons/leak.png"
            thumbnail_filename = "leak.png"
            embed_message.set_thumbnail(url=f"attachment://{thumbnail_filename}")

            with open(thumbnail_path, "rb") as file:
                message = await channel.send(
                    content=f"{interaction.user.mention} submitted a leak:",
                    embed=embed_message,
                    file=discord.File(file, filename=thumbnail_filename)
                )
                await message.edit(view=LeaksView(message))

            await interaction.response.send_message(f"{interaction.user.mention} Thank you for submitting a leak, it will be dealt with!", ephemeral=True, delete_after=settings.DELETE_AFTER)
        except Exception as e:
            await interaction.response.send_message(f"_Error submitting a leak, contact staff {e}_", ephemeral=True, delete_after=settings.DELETE_AFTER)
import discord

class FormatView(discord.ui.View):
    def __init__(self, originalInteraction: discord.Interaction, embed: discord.Embed):
        super().__init__(timeout=None)
        
        self.originalInteraction = originalInteraction
        self.embed = embed

    @discord.ui.button(label="OK", style=discord.ButtonStyle.green)
    async def ok(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.originalInteraction.delete_original_response()
        
        thumbnail_path = "resources/icons/megaphone.png"
        thumbnail_filename = "megaphone.png"
        with open(thumbnail_path, "rb") as file:
            await interaction.channel.send(embed=self.embed, file=discord.File(file, filename=thumbnail_filename))
        
    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray)
    async def edit(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_modal(FormatModal(initialTitle=self.embed.title, initialMessage=self.embed.fields[0].value))
        await self.originalInteraction.delete_original_response()
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.originalInteraction.delete_original_response()

class FormatModal(discord.ui.Modal, title="Enter Your Message"):
    def __init__(self, initialTitle="", initialMessage=""):
        super().__init__()
        self.msgTitle = discord.ui.TextInput(
            label="Title",
            style=discord.TextStyle.short,
            placeholder="Title...",
            required=True,
            max_length=30,
            default=initialTitle
        )
        
        self.message = discord.ui.TextInput(
            label="Message",
            style=discord.TextStyle.paragraph,
            placeholder="Type your message here...",
            required=True,
            max_length=2000,
            default=initialMessage
        )
        
        self.add_item(self.msgTitle)
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        embed_message = discord.Embed(title=self.msgTitle.value, color=discord.Color.gold())
        embed_message.set_author(name=f"{interaction.user.display_name}", icon_url=interaction.user.avatar)
        embed_message.add_field(name="", value=self.message.value, inline=False)
        
        view = FormatView(interaction, embed_message)
        
        thumbnail_path = "resources/icons/megaphone.png"
        thumbnail_filename = "megaphone.png"
        embed_message.set_thumbnail(url=f"attachment://{thumbnail_filename}")

        with open(thumbnail_path, "rb") as file:
            await interaction.response.send_message(f"Preview:", ephemeral=True, embed=embed_message, view=view, file=discord.File(file, filename=thumbnail_filename))
        
        
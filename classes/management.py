import discord
import util
import settings

class SetupView(discord.ui.View):
    def __init__(self, originalInteraction: discord.Interaction):
        super().__init__(timeout=None)
        
        self.originalInteraction = originalInteraction
        
        self.user_select = UserSelect()
        self.hardcoded_select = RoleSelect()
        
        self.add_item(self.user_select)
        self.add_item(self.hardcoded_select)

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.user_select.values:
            await interaction.response.send_message("No user selected!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        if not self.hardcoded_select.values:
            await interaction.response.send_message("No role selected!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        #Get category based on role
        selectedRole = self.hardcoded_select.values[0]
        selected_user = self.user_select.values[0]
        
        category = util.getCategoryByName(interaction.guild ,selectedRole)
        if not category:
            await interaction.response.send_message("No such category!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        #Check if channel with username already exists, if not create voice + text
        if util.findChannelsByNameInCategory(category=category, word=selected_user.name) is not None:
            await interaction.response.send_message("That user is already setup!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        await interaction.guild.create_text_channel(selected_user.name + " -❌", category=category)
        await interaction.guild.create_text_channel(f"{selected_user.name}-schedule", category=category)
        await interaction.response.send_message(f"Successfully setup channels for {selected_user.display_name} in {selectedRole} category!", delete_after=settings.DELETE_AFTER, ephemeral=True)
        
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.user_select.values:
            await interaction.response.send_message("No user selected!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        if not self.hardcoded_select.values:
            await interaction.response.send_message("No role selected!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        #Get category based on role
        selectedRole = self.hardcoded_select.values[0]
        selected_user = self.user_select.values[0]
        
        category = util.getCategoryByName(interaction.guild ,selectedRole)
        if not category:
            await interaction.response.send_message("No such category!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        channels = util.findChannelsByNameInCategory(category=category, word=selected_user.name)
        if channels is None:
            await interaction.response.send_message("That user does not have channels set up!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        for channel in channels:
            await channel.delete()
            
        await interaction.response.send_message(f"Successfully deleted channels for {selected_user.display_name} in {selectedRole} category!", delete_after=settings.DELETE_AFTER, ephemeral=True)
        
    @discord.ui.button(label="Done", style=discord.ButtonStyle.gray)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.originalInteraction.delete_original_response()
        

class UserSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select a user", min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class RoleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Supervisor", value="Supervisor"),
            discord.SelectOption(label="Manager", value="Manager"),
            discord.SelectOption(label="Consultant", value="Consultant")
        ]
        super().__init__(placeholder="Select a role", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

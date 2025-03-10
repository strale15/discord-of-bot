from logging import Logger
import discord
import util
import settings

class SetupView(discord.ui.View):
    def __init__(self, originalInteraction: discord.Interaction, log: Logger):
        super().__init__(timeout=None)
        
        self.originalInteraction = originalInteraction
        self.log = log
        
        self.user_select = UserSelect()
        self.hardcoded_select = RoleSelect()
         
        self.add_item(self.user_select)
        self.add_item(self.hardcoded_select)
        

    @discord.ui.button(label="Setup 'clock in' channel", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.user_select.values:
            await interaction.response.send_message("No user selected!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        if not self.hardcoded_select.values:
             await interaction.response.send_message("No role selected!", delete_after=settings.DELETE_AFTER, ephemeral=True)
             return
         
        #Get category based on role
        selected_category_id = self.hardcoded_select.values[0]
        selected_user = self.user_select.values[0]
        
        category = await interaction.guild.fetch_channel(selected_category_id)
        if not category:
            await interaction.response.send_message("No such category!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        #Check if channel with username already exists, if not create text clock in channel
        channel = await util.findClockInChannelByUsername(guild=interaction.guild, username=selected_user.display_name)
        if channel is not None:
            await interaction.response.send_message("That user is already setup!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        await interaction.guild.create_text_channel(selected_user.display_name + " -❌", category=category)
        await interaction.response.send_message(f"Successfully setup channel for {selected_user.display_name}!", delete_after=settings.DELETE_AFTER, ephemeral=True)
        
    @discord.ui.button(label="Delete 'clock in' channel", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.user_select.values:
            await interaction.response.send_message("No user selected!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
         
        #Get category based on role
        selected_user = self.user_select.values[0]
        
        channel = await util.findClockInChannelByUsername(guild=interaction.guild, username=selected_user.display_name)
        if channel is None:
            await interaction.response.send_message("That user does not have channels set up!", delete_after=settings.DELETE_AFTER, ephemeral=True)
            return
        
        await channel.delete()
        try:
            await interaction.response.send_message(f"Successfully deleted clock in channel for {selected_user.display_name}!", delete_after=settings.DELETE_AFTER, ephemeral=True)
        except:
            self.log.info("Unknown interaction after delete")
        
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
            discord.SelectOption(label="Supervisor", value=settings.M_SUPERVISOR_CLOCK_CATEGORY),
            discord.SelectOption(label="Management", value=settings.M_MANAGEMENT_CLOCK_CATEGORY),
            discord.SelectOption(label="Consultant", value=settings.M_CONSULTANT_CLOCK_CATEGORY),
            discord.SelectOption(label="MPPV Engineer", value=settings.M_MPPV_ENG_CLOCK_CATEGORY)
        ]
        super().__init__(placeholder="Select a role", min_values=1, max_values=1, options=options)
 
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

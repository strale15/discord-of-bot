from sqlite3 import Date
from venv import logger
import util
import discord
import settings
from classes import sheets
from datetime import datetime

class FineModal(discord.ui.Modal, title="Fine an employee"):
    def __init__(self):
        super().__init__(title="Fine an employee")    

        self.username = discord.ui.TextInput(
            label="Discord username:",
            placeholder= "someuser1312",
            required=True,
            min_length=1,
            max_length=30,
            style=discord.TextStyle.short,
        )
        
        self.amount = discord.ui.TextInput(
            label="Fine amount in $:",
            placeholder= "100",
            required=True,
            min_length=1,
            max_length=5,
            style=discord.TextStyle.short,
        )
        
        self.reason = discord.ui.TextInput(
            label="Reason:",
            placeholder="details...",
            required=True,
            min_length=1,
            max_length=100,
            style=discord.TextStyle.paragraph,
        )
        
        # Add the field to the modal
        self.add_item(self.username)
        self.add_item(self.amount)
        self.add_item(self.reason)

    
async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()  # This prevents interaction expiration
    
    try:
        user = discord.utils.get(interaction.guild.members, name=self.username.value)
        
        if user is None:
            await interaction.followup.send(f"_User with that username doesn't exist_", ephemeral=True, delete_after=settings.DELETE_AFTER)
            return
        
        now = datetime.now()
        current_date = f"{now.month}/{now.day}/{now.year}"
        sheets.addFine(username=self.username.value, reason=self.reason.value, amount=int(self.amount.value), date=current_date)
        
        await interaction.followup.send(f"{user.mention} you have been fined **{self.amount.value}$**, reason: _{self.reason.value}_")
    
    except Exception as e:
        await interaction.followup.send(f"_Error submitting a fine, contact staff {e}_", ephemeral=True, delete_after=settings.DELETE_AFTER)

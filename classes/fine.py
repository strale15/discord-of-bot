from sqlite3 import Date
from venv import logger
import util
import discord
import settings
from classes import sheets
from datetime import datetime
import asyncio

async def delete_message_after_delay(message: discord.Message, delay: int):
    await asyncio.sleep(delay)
    await message.delete()

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
    await interaction.response.defer(ephemeral=True)
    
    try:
        user = discord.utils.get(interaction.guild.members, name=self.username.value)
        
        if user is None:
            message = await interaction.followup.send(f"_User with that username doesn't exist_", ephemeral=True)
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
            return
        
        now = datetime.now()
        current_date = f"{now.month}/{now.day}/{now.year}"
        sheets.addFine(username=self.username.value, reason=self.reason.value, amount=int(self.amount.value), date=current_date)
        
        await interaction.channel.send(f"{user.mention} you have been fined **{self.amount.value}$**, reason: _{self.reason.value}_", ephemeral=False)
        await interaction.followup.send(f"_{user.name} has been fined_", ephemeral=True)
    
    except Exception as e:
        message = await interaction.followup.send(f"_Error submitting a fine, contact staff {e}_", ephemeral=True)
        asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))

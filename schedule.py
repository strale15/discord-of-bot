from logging import Logger
import string
import discord
from discord.ext import tasks
import datetime
from datetime import datetime as dt
import settings
from discord.ext import commands
import pytz

timezone = pytz.timezone("America/Chicago")

class Scheduler:
    def __init__(self, bot: commands.Bot, log: Logger):
        self.bot = bot
        self.log = log
        self.offday_msg = self.read_announcement_from_file('offDayMsg.txt')
        self.payment_msg = self.read_announcement_from_file('paymentMsg.txt')
        self.task.start()

        self.last_sent_minute_offday = None
        self.last_sent_minute_payment = None

    @tasks.loop(seconds=20)
    async def task(self):
        now = dt.now(timezone)
        current_time = now.strftime("%H:%M")
        
        #OffDayRequest
        if current_time == settings.OFF_DAY_SEND_TIME and now.weekday() == 4 and current_time != self.last_sent_minute_offday:
            self.log.info(f"Entered a offday task at {now}")
            await self.publish_announcement(msg=self.offday_msg)
            self.last_sent_minute_offday = current_time
        elif current_time != self.last_sent_minute_offday:
            self.last_sent_minute_offday = None
            
        #Payment notice
        if now.day == 25 and current_time == settings.PAYMENT_SEND_TIME and current_time != self.last_sent_minute_payment:
            self.log.info(f"Entered a payment task at {now}")
            await self.publish_announcement(msg=self.payment_msg)
            self.last_sent_minute_payment = current_time
        elif current_time != self.last_sent_minute_payment:
            self.last_sent_minute_payment = None
            

    async def publish_announcement(self, msg: str):
        guild = self.bot.get_guild(settings.ANNOUNCEMENT_GUILD_ID_INT)

        if not guild:
            self.log.error("Failed to find the guild.")
            return

        channel = guild.get_channel(settings.ANNOUNCEMENT_CHANNEL_ID)
        if not channel:
            self.log.error("Failed to get announcement channel")
            return

        if not channel.is_news():
            self.log.error("Provided channel is not an announcement channel")
            return

        message_to_publish = await channel.send(msg)
        await message_to_publish.publish()

    def read_announcement_from_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            self.log.error(f"Announcement file '{filepath}' not found!")
            return "No announcement message found."
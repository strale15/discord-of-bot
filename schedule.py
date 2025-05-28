from logging import Logger
from math import e
import string
import discord
from discord.ext import tasks
import datetime
from datetime import datetime as dt
import settings
from discord.ext import commands
import pytz
import calendar
from customlist import LinkedListQueue
import util
from classes import database

timezone = pytz.timezone("America/Chicago")

mm_time_queue = LinkedListQueue()

def replace_month_name(msg: str, now) -> str:
    next_month_number = (now.month + 1) % 12
    next_month_name = calendar.month_name[next_month_number]
    
    return msg.replace("#month", next_month_name)

class Scheduler:
    def __init__(self, bot: commands.Bot, log: Logger):
        self.bot = bot
        self.log = log
        self.offday_msg = self.read_announcement_from_file('resources/offDayMsg.txt')
        self.payment_msg = self.read_announcement_from_file('resources/paymentMsg.txt')
        
        self.task.start()
        self.mmPing.start()
        self.pingChatters.start()

        self.last_ping_time = None
        self.last_sent_minute_offday = None
        self.last_sent_minute_payment = None

    @tasks.loop(seconds=60)
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
        if now.day == settings.PAYMENT_SEND_DAY and current_time == settings.PAYMENT_SEND_TIME and current_time != self.last_sent_minute_payment:
            self.log.info(f"Entered a payment task at {now}")
            
            messageWithMonth = replace_month_name(self.payment_msg, now=now)
            await self.publish_announcement(msg=messageWithMonth)
            self.last_sent_minute_payment = current_time
        elif current_time != self.last_sent_minute_payment:
            self.last_sent_minute_payment = None
            
            
    @tasks.loop(seconds=15)
    async def mmPing(self):
        if mm_time_queue.peek() == None:
            return
        
        now = dt.now()
        
        if self.last_ping_time != None and (now - self.last_ping_time).total_seconds() / 60.0 < settings.MM_MIN_PING:
            return
        
        m_id, oldest_mm_time = mm_time_queue.peek()
        
        if (now - oldest_mm_time).total_seconds() / 60.0 > settings.MM_MIN_WAIT:
            await self.pingMM()
            self.last_ping_time = now
            mm_time_queue.pop()
            
            self.log.info(f"Pinged mm at {now}, id: {m_id}")
            
            
    @tasks.loop(seconds=60)
    async def pingChatters(self):
        unsent_mms = database.get_old_pings(settings.CHATTER_MM_PING_TIME)
        for chatter_id, model_channel_id in unsent_mms:
            try:
                await self.pingChatterMM(chatter_id=int(chatter_id), model_channel_id=int(model_channel_id))
                database.delete_ping(chatter_id=chatter_id, model_channel_id=model_channel_id)
            except Exception as e:
                print(f"Error pinging {chatter_id} for {model_channel_id} error: {e}")
                
            
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
        
    async def pingMM(self):
        guild = self.bot.get_guild(settings.GUILD_ID_INT)
        mm_channel = discord.utils.get(guild.channels, id=settings.MMA_APPROVAL_ID)
        
        consultantRole = discord.utils.get(guild.roles, id=settings.CONSULT_ROLE_ID)
        managementRole = discord.utils.get(guild.roles, id=settings.MANAGEMENT_ROLE_ID)
        supervisorRole = discord.utils.get(guild.roles, id=settings.SUPERVISOR_ROLE_ID)
        ppvRole = discord.utils.get(guild.roles, id=settings.PPV_ENG_ROLE_ID)
        
        await mm_channel.send(f"{consultantRole.mention} {managementRole.mention} {supervisorRole.mention} {ppvRole.mention}", delete_after=settings.DELETE_PING_AFTER)
        
    async def pingChatterMM(self, chatter_id, model_channel_id):
        guild = self.bot.get_guild(settings.GUILD_ID_INT)
        mm_channel = discord.utils.get(guild.channels, id=model_channel_id)
        user = discord.utils.get(guild.members, id=chatter_id)
        
        await mm_channel.send(f"{user.mention} _you clocked in {settings.CHATTER_MM_PING_TIME} minutes ago and haven't sent a mass message for approval, please do._")
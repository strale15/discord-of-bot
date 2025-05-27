from discord.ext import commands
import settings
import datetime
import discord
from discord.ext import commands

import settings
from classes import sheets, database
from util import *
import ndacheck
import util
import os

log = settings.logging.getLogger()
user_cooldowns = {}
COOLDOWN_TIME = datetime.timedelta(minutes=settings.SEND_NDA_COOLDOWN)

pdf_user_cooldowns = {}
COOLDOWN_PDF_TIME = datetime.timedelta(minutes=settings.SEND_NDA_PDF_COOLDOWN)     

class NdaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        
    @commands.Cog.listener()
    async def on_member_join(member: discord.Member):
        if member.guild.id != settings.TRAIN_GUILD_ID_INT:
            return
        
        if not member.bot:
            if database.is_nda_signed(member.id):
                return
            
            join_message = f"""Hello {member.global_name} and welcome to XICE.

In this server you will go through the process of learning one of the highest degrees of OnlyFans chatting and the opportunities that lie ahead for you once you start your journey. As this is a fully remote job, this can be done anywhere in the world, so long as you have a stable internet connection and a computer that can run Infloww.

We look forward to seeing the fullest extent of your abilities very soon!

**Please fill in this form: https://forms.gle/jyGAT1eDR9RrktZk7**

Once you're done respond with **'Send NDA'**, I will send you the NDA to sign so you can start with the trainings.
-# If you are unable to send messages to a bot try using Discord App, not the browser."""
            
            try:
                await member.send(join_message)
            except discord.Forbidden:
                log.info(f"Could not send a join DM to {member.name}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if isinstance(message.channel, discord.DMChannel) and message.content.lower() == "send nda":
            user_id = message.author.id
            
            if database.is_nda_signed(user_id):
                await message.channel.send(f"You have already signed the NDA.")
                return
            
            #Check google forms
            if not sheets.is_form_filled(message.author.name):
                fill_form_msg = """Please fill in the google form (https://forms.gle/jyGAT1eDR9RrktZk7).
If you've already done so, you might've made typos on your submission. In this case, please go back to your submitted form and **ensure** that all details are correct, especially details regarding your Discord **username**.

Once this is done, respond with **'Send NDA'** once more for me to send you the NDA to sign."""
                
                await message.channel.send(fill_form_msg)
                return
            
            if user_id in user_cooldowns:
                last_sent_time = user_cooldowns[user_id]
                current_time = datetime.datetime.now()

                if current_time - last_sent_time < COOLDOWN_TIME:
                    remaining_time = COOLDOWN_TIME - (current_time - last_sent_time)
                    await message.channel.send(f"Please wait {remaining_time} before requesting the NDA again.")
                    return
            
            temp_pdf = ndacheck.edit_nda_date()
            
            try:
                watch_nda_msg = """Please watch the video on how to sign the NDA. Once you're done, submit the file to me in this chat and you're all good to go!
Make sure to rename your NDA file as such: **XIC_NDA-Name_Surname.pdf**
For example: **XIC_NDA-John_Doe.pdf**
_Also don't use special characters like ć,č,ž,ä,ö... and similar._
https://www.sejda.com/pdf-editor"""
                
                await message.channel.send(watch_nda_msg)
                await message.channel.send(file=discord.File(temp_pdf))
                await message.channel.send(file=discord.File("nda/guide.mp4"))
            finally:
                if os.path.exists(temp_pdf):
                    os.remove(temp_pdf)
            
            user_cooldowns[user_id] = datetime.datetime.now()

        if isinstance(message.channel, discord.DMChannel) and message.attachments:
            for attachment in message.attachments:
                if attachment.filename.endswith(".pdf") and "XIC_NDA" not in attachment.filename:
                    await message.channel.send(f"I received your PDF but please name it accordingly '**XIC_NDA-Name_Surname.pdf**'")
                
                if attachment.filename.endswith(".pdf") and "XIC_NDA" in attachment.filename:
                    user_id = message.author.id
            
                    if database.is_nda_signed(user_id):
                        await message.channel.send(f"You have already signed the NDA.")
                        return
                    
                    #Check google forms
                    if not sheets.is_form_filled(message.author.name):
                        fill_form_msg = """Please fill in the google form (https://forms.gle/jyGAT1eDR9RrktZk7) before sending the signed NDA.
If you've already done so, you might've made typos on your submission. In this case, please go back to your submitted form and **ensure** that all details are correct, especially details regarding your Discord **username**.

Once this is done, respond with **'Send NDA'** once more for me to send you the NDA to sign."""
                        
                        await message.channel.send(fill_form_msg)
                        return
            
                    if user_id in pdf_user_cooldowns:
                        last_sent_time = pdf_user_cooldowns[user_id]
                        current_time = datetime.datetime.now()

                        if current_time - last_sent_time < COOLDOWN_PDF_TIME:
                            remaining_time = COOLDOWN_PDF_TIME - (current_time - last_sent_time)
                            await message.channel.send(f"Please wait {remaining_time} before sending the NDA pdf again.")
                            return
                    
                    date = datetime.datetime.now()
                    formatted_date = date.strftime("%Y-%m-%d")
                    file_path = f"./nda/{formatted_date}_{user_id}_{attachment.filename}"
                    await attachment.save(file_path)
                    pdf_user_cooldowns[user_id] = datetime.datetime.now()
                    
                    #Check pdf for name and signature
                    check, err_msg, full_name = ndacheck.checkNda(path=file_path)
                    if check:
                        #Save to drive and give role to the user
                        try:
                            ndacheck.upload_to_drive(file_path=file_path, folder_id=settings.DRIVE_FOLDER_ID)
                            database.sign_nda(user_id=user_id, discord_nick=message.author.name, full_name=full_name)
                            await message.channel.send("Great, the NDA looks properly filled out. Welcome to XICE Training!")
                            
                            if await util.assign_role_by_ids(self.bot, settings.TRAIN_GUILD_ID_INT, user_id, settings.TRAINEE_ROLE_ID):
                                if await util.assign_role_by_ids(self.bot, settings.TRAIN_GUILD_ID_INT, user_id, settings.NDA_SIGNED_ROLE_ID):
                                    await util.remove_role_by_ids(self.bot, settings.TRAIN_GUILD_ID_INT, user_id, settings.WELCOME_ROLE_ID)
                                    await message.channel.send("You have received the Trainee role and can begin your training process. Please **ensure** that you're reading **ALL** channels available to you, and reacting to get your appropriate Training Shift Roles. Failure to follow said procedures will result in a kick from the server within **3 days** after joining.")
                            else:
                                await message.channel.send("Something went wrong while assigning you the Trainee role, please contact management.")
                        except Exception as e:
                            log.warning(e)
                            await message.channel.send("Something went wrong while processing your NDA, please contact management.")
                    else:
                        await message.channel.send(f"{err_msg}")
                    
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        log.warning(f"Error deleting file: {e}")
                break

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(NdaCog(bot))
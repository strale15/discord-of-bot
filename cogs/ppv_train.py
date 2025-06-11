import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random
import re

import settings
from util import *
import util
from classes import ppv_train_db as db
from classes import mm_train_db as mmdb
from classes import ppvSheet as ppvsheet

class TrainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.started_example = []
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not isinstance(message.channel, discord.DMChannel):
            return
            
        #START hw
        match = re.match(r"^start\s+(ctx_[0-9]{3})\s*$", message.content.lower())
        if match:
            img_id = match.group(1)
            trainee_id = message.author.id
            
            if not db.is_hw_startable(img_id, trainee_id):
                await message.channel.send(f"This code was either not assigned to you/you have already completed it/you already started it.")
                return
            
            ppv_hw_instruction = f"""Write a PPV for this scenario by sending ma a message in the following format format:
end {img_id}

PPV caption

PPV followup

self rate 1-10
"""
            db.start_hw(img_id, trainee_id)
            
            file_id = util.getCtxImgDriveId(img_id=img_id)
            embed = discord.Embed(title="PPV scenario image:", description="*(if empty please wait for it to load...)*")
            embed.set_image(url=f"https://drive.google.com/uc?export=view&id={file_id}")
            await message.channel.send(ppv_hw_instruction, embed=embed)
            return
            
        #END hw
        lines = message.content.splitlines()
        first_line = lines[0].lower()
        last_line = lines[-1].lower()
        
        match_first = re.match(r"^end\s+(ctx_[0-9]{3})\s*$", first_line)
        match_last = re.match(r"^self rate ([0-9]{1,2})\s*$", last_line)
        if match_first:
            if not match_last:
                await message.channel.send(f"Please provide a self rate from 1-10 at the end, for example _self rate 6_")
                return
            
            self_rate = match_last.group(1)
            if int(self_rate) < 1 or int(self_rate) > 10:
                await message.channel.send(f"Please keep the self rate in range 1-10.")
                return
            
            img_id = match_first.group(1)
            trainee_id = message.author.id
            
            if len(lines) < 3:
                await message.channel.send(f"You are trying to submit an empty response for homework code {img_id}.")
                return
            
            response = "\n".join(lines[1:-1]).strip()
            
            if not db.is_hw_in_progress(img_id, trainee_id):
                await message.channel.send(f"You either completed this homework or have not started it yet. Send me 'start [code]' if you want to start it.")
                return
            
            #Submit hw
            msg = await message.channel.send(f"_Submitting, please wait..._")
            schedule_date, img_id, trainee_id, completion_time, response = db.end_hw(img_id, trainee_id, response, int(self_rate))
            
            completion_time_minutes = int(completion_time // 60)
            completion_time_seconds = round(completion_time % 60)
            completion_time_str = f"{completion_time_minutes}m {completion_time_seconds}s"
            
            discord_display_name = await util.get_train_guild_display_name_from_user_id(self.bot, trainee_id)
            date = schedule_date.strftime("%Y-%m-%d %H:%M")
            
            ppvsheet.submit_hw_to_sheet(date, img_id, discord_display_name, trainee_id, completion_time_str, response, self_rate)
            
            await msg.edit(content=f"Thanks for submitting the homework code **{img_id}**. Your response was recorded.")
            return
        
        #Start HW example
        if message.content.lower().strip() == "start ctx_example":     
            ppv_hw_instruction = f"""Write a PPV for this scenario (**ctx_example**), in format:
end [code] <- You will wirte an actual homework code like ctx_001 or in this case ctx_example

PPV caption <- Here you write PPV caption

PPV followup <- Here you write the PPV followup

self rate 1-10 <- Here you provide a rate for you ppv from 1-10
"""
            file = discord.File("resources/training/context_example/ctx_example.png", filename="ctx_example.png")
            embed = discord.Embed(title="PPV scenario image:")
            embed.set_image(url="attachment://ctx_example.png")
            await message.channel.send(ppv_hw_instruction, embed=embed, file=file)
            
            ppv_hw_instruction = f"""
*For the example above^ you would submit your response like:*

end ctx_example

some ppv caption

some ppv followup

self rate 5
"""
            await message.channel.send(ppv_hw_instruction)
            return
            
        #End HW example
        first_line = message.content.splitlines()[0].lower()
        if first_line == "end ctx_example":
            lines = message.content.splitlines()
            
            if len(lines) < 2:
                await message.channel.send(f"You successfully ended hw example but your ppv caption and followup are probably missing.")
                return
            
            await message.channel.send(f"Thanks for submitting the homework code **ctx_example**. Your successfully completed ppv example.")
            return
        
        #Show unfinished hw
        if message.content.lower() == "hw?":
            trainee_id = message.author.id
            img_codes = db.get_not_started_hw_for_trainee_id(trainee_id)  
            
            msg = ""
            if img_codes is None or len(img_codes) == 0:
                msg = f"You currently do not have any PPV homeworks assigned to you."
            else:
                codes_str = ", ".join(img_codes)
                msg = f"Following PPV homework codes are assigned to you and incomplete: **{codes_str}**"
            
            img_codes_started = db.get_started_hw_for_trainee_id(trainee_id)
            if img_codes_started is not None and len(img_codes_started) > 0:
                codes_str_started = ", ".join(img_codes_started)
                msg += f"\nYou also started but never ended the following PPV homework codes: **{codes_str_started}**, please do."
                
            left_mms_tuple = mmdb.get_left_mm_for_trainee_id(trainee_id)
            if left_mms_tuple is not None and len(left_mms_tuple) > 0:
                for hw_id, mms_left in left_mms_tuple:
                    msg += f"\nYou haven't completed MM homework with id **{hw_id}** (*{mms_left} mms left to submit*)"
            else:
                msg += f"\nYou currently do not have any MM homeworks assigned to you."
            
            await message.channel.send(msg)
            return
        
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.command(name="hw-ppv", description="Gives homework to trainees that are in the same voice call as you")
    async def givePpvHomework(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        trainer_role = interaction.guild.get_role(settings.TRAINER_ROLE_ID)
        if trainer_role not in interaction.user.roles:
            await interaction.followup.send("You do not have a _Trainer_ role.")
            return
        
        trainees = await util.extract_trainees_from_voice(interaction)
        
        if trainees is not None and len(trainees) > 0:
            for trainee in trainees:
                await self.generate_ppv_hw_for_trainee(trainee)
            message = await interaction.followup.send("Successfully generated PPV homework for all trainees.")
            asyncio.create_task(delete_message_after_delay(message, settings.DELETE_AFTER))
    
    async def generate_ppv_hw_for_trainee(self, trainee: discord.Member):
        img_codes = []
        existing_img_ids = db.get_img_ids_for_trainee(trainee.id)
        
        for i in range(3):
            img_id = self.generate_random_img_id(existing_img_ids)
            
            if img_id is None:
                break
                
            img_codes.append(img_id)
            db.insert_ppv_train(img_id=img_id, trainee_id=trainee.id)
        
        if len(img_codes) == 0:
            await util.send_dm(trainee, "Congrats, you have completed all available ppv homeworks for now!")
            return
            
        codes_str = ", ".join(img_codes)
        hw_msg = f"""Homework with the following codes was generated for you: **{codes_str}**.
When you are ready to start one of the homeworks send **start [code]** for example **start {img_codes[0]}**.

_Note:_ These responses are **timed**!

-# *If this is your first time doing the homework or you forgot how to do it you can go trough an example just send **start ctx_example**.*
"""
        await util.send_dm(trainee, hw_msg)
            
    def generate_random_img_id(self, existing_img_ids):
        num_of_ctx_imgs = util.countContextImages()
        if len(existing_img_ids) >= num_of_ctx_imgs:
            return None
        
        while True:
            num = random.randint(1, num_of_ctx_imgs)
            img_id = f"ctx_{num:03}"
            if img_id not in existing_img_ids:
                return img_id
        
    async def cog_load(self):
        self.bot.tree.add_command(self.givePpvHomework, guild=settings.TRAIN_GUILD_ID)

async def setup(bot):
    await bot.add_cog(TrainCog(bot))
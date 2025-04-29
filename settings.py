import pathlib
import os
from logging.config import dictConfig
from dotenv import load_dotenv
import discord
import logging

load_dotenv()

LINE_TEXT = "**---------------------------------------------------------------------------------**"

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")

BASE_DIR = pathlib.Path(__file__).parent

CMDS_DIR = BASE_DIR / "cmds"
COGS_DIR = BASE_DIR / "cogs"

VIDEOCMDS_DIR = BASE_DIR / "videocmds"

CROSS_EMOJI = "❌"
TICK_EMOJI = "✅"

DELETE_AFTER = int(os.getenv("DELETE_AFTER"))

SHEET_ID = os.getenv("SHEET_ID")
TRAIN_FORM_SHEET_ID = os.getenv("TRAIN_FORM_SHEET_ID")

#PROD
GUILD_ID_INT = int(os.getenv("GUILD_ID"))
GUILD_ID = discord.Object(id=GUILD_ID_INT)

M_GUILD_ID_INT = int(os.getenv("M_GUILD_ID"))
M_GUILD_ID = discord.Object(id=M_GUILD_ID_INT)

MMA_APPROVAL_ID = int(os.getenv("MMA_APPROVAL_ID"))
CUSTOMS_QUEUE_ID = int(os.getenv("CUSTOMS_QUEUE_ID"))
VOICE_QUEUE_ID = int(os.getenv("VOICE_QUEUE_ID"))
LEAKS_QUEUE_ID = int(os.getenv("LEAKS_QUEUE_ID"))
FINES_CHANNEL_ID = int(os.getenv("FINES_CHANNEL_ID"))

CONSULT_ROLE_ID = int(os.getenv("CONSULT_ROLE_ID"))
SUPERVISOR_ROLE_ID = int(os.getenv("SUPERVISOR_ROLE_ID"))
PPV_ENG_ROLE_ID = int(os.getenv("PPV_ENG_ROLE_ID"))
MANAGEMENT_ROLE_ID = int(os.getenv("MANAGEMENT_ROLE_ID"))

M_MANAGEMENT_ROLE_ID = int(os.getenv("M_MANAGEMENT_ROLE_ID"))
M_SUPERVISOR_ROLE_ID = int(os.getenv("M_SUPERVISOR_ROLE_ID"))
M_PPV_ENG_ROLE_ID = int(os.getenv("M_PPV_ENG_ROLE_ID"))
M_CONSULTANT_ROLE_ID = int(os.getenv("M_CONSULTANT_ROLE_ID"))

M_MANAGEMENT_CLOCK_CHANNEL = int(os.getenv("M_MANAGEMENT_CLOCK_CHANNEL"))
M_SUPERVISOR_CLOCK_CHANNEL = int(os.getenv("M_SUPERVISOR_CLOCK_CHANNEL"))
M_PPV_ENG_CLOCK_CHANNEL = int(os.getenv("M_PPV_ENG_CLOCK_CHANNEL"))
M_CONSULTANT_CLOCK_CHANNEL = int(os.getenv("M_CONSULTANT_CLOCK_CHANNEL"))

#Announcement
ANNOUNCEMENT_GUILD_ID_INT = int(os.getenv("ANNOUNCEMENT_GUILD_ID"))
ANNOUNCEMENT_GUILD_ID = discord.Object(id=ANNOUNCEMENT_GUILD_ID_INT)
ANNOUNCEMENT_CHANNEL_ID = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID"))

OFF_DAY_SEND_TIME = os.getenv("OFF_DAY_SEND_TIME")
PAYMENT_SEND_TIME = os.getenv("PAYMENT_SEND_TIME")
PAYMENT_SEND_DAY = int(os.getenv("PAYMENT_SEND_DAY"))

#Ping management
MM_MIN_PING = float(os.getenv("MM_MIN_PING"))
MM_MIN_WAIT = float(os.getenv("MM_MIN_WAIT"))
DELETE_PING_AFTER = int(os.getenv("DELETE_PING_AFTER"))

#Train
TRAIN_GUILD_ID_INT = int(os.getenv("TRAIN_GUILD_ID"))
TRAIN_GUILD_ID = discord.Object(id=TRAIN_GUILD_ID_INT)

TRAINEE_ROLE_ID = int(os.getenv("TRAINEE_ROLE_ID"))

SEND_NDA_COOLDOWN = int(os.getenv("SEND_NDA_COOLDOWN"))
SEND_NDA_PDF_COOLDOWN = int(os.getenv("SEND_NDA_PDF_COOLDOWN"))

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

#Chatter mm ping
CHATTER_MM_PING_TIME = int(os.getenv("CHATTER_MM_PING_TIME"))

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
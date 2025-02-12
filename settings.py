import pathlib
import os
from logging.config import dictConfig
from dotenv import load_dotenv
import discord
import logging

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")

BASE_DIR = pathlib.Path(__file__).parent

CMDS_DIR = BASE_DIR / "cmds"
COGS_DIR = BASE_DIR / "cogs"

VIDEOCMDS_DIR = BASE_DIR / "videocmds"

DELETE_AFTER = int(os.getenv("DELETE_AFTER"))

SHEET_ID = os.getenv("SHEET_ID")

#DEV
GUILD_ID_INT_DEV = int(os.getenv("GUILD_ID_DEV"))
GUILD_ID_DEV = discord.Object(id=GUILD_ID_INT_DEV)

MMA_APPROVAL_ID_DEV = int(os.getenv("MMA_APPROVAL_ID_DEV"))
CUSTOMS_QUEUE_ID_DEV = int(os.getenv("CUSTOMS_QUEUE_ID_DEV"))
VOICE_QUEUE_ID_DEV = int(os.getenv("VOICE_QUEUE_ID_DEV"))
LEAKS_QUEUE_ID_DEV = int(os.getenv("LEAKS_QUEUE_ID_DEV"))
FINES_CHANNEL_ID_DEV = int(os.getenv("FINES_CHANNEL_ID_DEV"))

CONSULT_ID_DEV = int(os.getenv("CONSULT_ID_DEV"))
SUPERVISOR_ID_DEV = int(os.getenv("SUPERVISOR_ID_DEV"))
PPV_ENG_ID_DEV = int(os.getenv("PPV_ENG_ID_DEV"))
MANAGEMENT_ROLE_ID_DEV = int(os.getenv("MANAGEMENT_ROLE_ID_DEV"))

#PROD
GUILD_ID_INT_PROD = int(os.getenv("GUILD_ID_PROD"))
GUILD_ID_PROD = discord.Object(id=GUILD_ID_INT_PROD)

MMA_APPROVAL_ID_PROD = int(os.getenv("MMA_APPROVAL_ID_PROD"))
CUSTOMS_QUEUE_ID_PROD = int(os.getenv("CUSTOMS_QUEUE_ID_PROD"))
VOICE_QUEUE_ID_PROD = int(os.getenv("VOICE_QUEUE_ID_PROD"))
LEAKS_QUEUE_ID_PROD = int(os.getenv("LEAKS_QUEUE_ID_PROD"))
FINES_CHANNEL_ID_PROD = int(os.getenv("FINES_CHANNEL_ID_PROD"))

CONSULT_ID_PROD = int(os.getenv("CONSULT_ID_PROD"))
SUPERVISOR_ID_PROD = int(os.getenv("SUPERVISOR_ID_PROD"))
PPV_ENG_ID_PROD = int(os.getenv("PPV_ENG_ID_PROD"))
MANAGEMENT_ROLE_ID_PROD = int(os.getenv("MANAGEMENT_ROLE_ID_PROD"))

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
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_ID = int(os.getenv("BOT_ID"))
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))
USERBOT_PREFIX = os.getenv("USERBOT_PREFIX")

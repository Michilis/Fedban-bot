import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))
SUDOERS = list(map(int, os.getenv("SUDOERS").split(',')))

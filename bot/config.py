import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Telegram bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# PostgreSQL database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Log group ID for logging actions
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))

# List of user IDs who have sudo privileges
SUDOERS = list(map(int, os.getenv("SUDOERS").split(',')))

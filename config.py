import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TOKEN = os.getenv('BOT_TOKEN')

# Debugging mode
DEBUGGING = os.getenv('DEBUGGING', 'False').lower() in ['true', '1', 't']

# Log group ID
LOG_GROUP_ID = int(os.getenv('LOG_GROUP_ID'))

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL')

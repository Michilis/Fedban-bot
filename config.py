import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TOKEN = os.getenv('TOKEN')

# Debugging mode
DEBUGGING = os.getenv('DEBUGGING', 'False').lower() in ['true', '1', 't']

# Other configurations can go here
LOG_GROUP_ID = int(os.getenv('LOG_GROUP_ID'))

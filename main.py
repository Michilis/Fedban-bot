import os
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

# Load the environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

app = Client(
    "my_bot",
    bot_token=BOT_TOKEN
)

# Add your modules
from modules import pmpermit, karma

if __name__ == "__main__":
    app.run()

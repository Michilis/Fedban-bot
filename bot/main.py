import sys
import os
import asyncio

# Ensure the bot directory is in the module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyrogram import Client
from config import BOT_TOKEN
from db import init_db

app = Client("fedban_bot", bot_token=BOT_TOKEN)

# Import commands and callbacks to register them
import bot.commands
import bot.callbacks

async def main():
    await init_db()
    await app.start()
    print("Bot is running...")
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())

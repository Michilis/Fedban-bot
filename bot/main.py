import sys
import os
import asyncio

# Ensure the root and bot directories are in the module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from bot.app import app  # Import the app instance from bot.app
from bot.db import init_db

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

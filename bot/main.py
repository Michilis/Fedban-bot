import sys
import os
import asyncio
from telegram.ext import Application

# Ensure the root and bot directories are in the module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from bot.app import app  # Import the app instance from bot.app
from bot.db import init_db
import bot.commands
import bot.callbacks

async def main():
    await init_db()
    bot.callbacks.register_help_handlers(app)
    await app.start_polling()
    print("Bot is running...")
    await asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    asyncio.run(main())

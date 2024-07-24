import asyncio
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

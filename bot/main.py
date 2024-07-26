# main.py
import asyncio
from bot.app import app
from bot.db import init_db
from bot.commands import register_command_handlers

async def main():
    await init_db()
    register_command_handlers(app)
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from telegram.ext import ApplicationBuilder
from bot.commands import register_command_handlers
from bot.callbacks import register_help_handlers
from config import BOT_TOKEN
from bot.db import init_db

async def main():
    await init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    register_command_handlers(app)
    register_help_handlers(app)
    await app.start()
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

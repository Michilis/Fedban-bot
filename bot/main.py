import asyncio
from telegram.ext import ApplicationBuilder
from bot.db import init_db
from bot.commands import register_command_handlers
from config import BOT_TOKEN

async def main():
    await init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    register_command_handlers(app)
    print("Bot is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.stop()
    await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

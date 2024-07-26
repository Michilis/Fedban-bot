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
    await app.updater.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(main())
    else:
        loop.run_until_complete(main())

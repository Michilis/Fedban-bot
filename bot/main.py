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
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e) == 'This event loop is already running':
            loop = asyncio.get_running_loop()
            loop.run_until_complete(main())
        else:
            raise

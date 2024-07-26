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
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())

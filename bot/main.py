import logging
import asyncio
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN, DEBUGGING
from bot.commands import register_command_handlers

if DEBUGGING:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    register_command_handlers(app)

    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    finally:
        loop.run_until_complete(main())

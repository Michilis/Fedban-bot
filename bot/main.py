import logging
import asyncio
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN, DEBUGGING
from bot.user_commands import register_user_command_handlers
from bot.admin_commands import register_admin_command_handlers
from bot.owner_commands import register_owner_command_handlers
from bot.callbacks import register_callback_handlers
from bot.db import init_db

if DEBUGGING:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

async def main():
    await init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    register_user_command_handlers(app)
    register_admin_command_handlers(app)
    register_owner_command_handlers(app)
    register_callback_handlers(app)

    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

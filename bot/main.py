import logging
import asyncio
from telegram.ext import ApplicationBuilder
from bot.user_commands import register_user_command_handlers
from bot.admin_commands import register_admin_command_handlers
from bot.owner_commands import register_owner_command_handlers
from config import TOKEN, DEBUGGING

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

if DEBUGGING:
    logger.setLevel(logging.DEBUG)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    register_user_command_handlers(app)
    register_admin_command_handlers(app)
    register_owner_command_handlers(app)
    
    async with app:
        logger.info("Bot is running...")
        await app.start()
        await app.updater.start_polling()
        await app.stop()
        await app.updater.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

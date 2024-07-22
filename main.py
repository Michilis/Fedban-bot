import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from modules import federation, help
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text("Hello! I'm the Fedban Bot. How can I help you today?")

async def error_handler(update, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    await update.message.reply_text('An error occurred. Please try again later.')

async def init_db():
    await federation.init_db(DATABASE_URL)

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    help.register_help_handlers(application)
    federation.register_federation_handlers(application)

    application.add_error_handler(error_handler)

    await init_db()

    logger.info("Starting bot...")
    await application.initialize()
    logger.info("Bot started, now polling updates...")
    await application.start_polling()

if __name__ == "__main__":
    asyncio.run(main())

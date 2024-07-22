import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from modules import federation, help

# Load environment variables from .env file
load_dotenv()

# Get configuration values
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

# Debug prints
print(f"BOT_TOKEN: {BOT_TOKEN}")
print(f"DATABASE_URL: {DATABASE_URL}")
print(f"LOG_GROUP_ID: {LOG_GROUP_ID}")

# Check if BOT_TOKEN is loaded correctly
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Please check your .env file.")

# Initialize the Telegram Bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start_bot():
    await federation.init_db(DATABASE_URL)
    print("Bot started successfully!")

    # Add handlers for federation commands
    app.add_handler(CommandHandler("newfed", federation.new_fed))
    app.add_handler(CommandHandler("joinfed", federation.join_fed))
    app.add_handler(CommandHandler("leavefed", federation.leave_fed))
    app.add_handler(CommandHandler("renamefed", federation.rename_fed))
    app.add_handler(CommandHandler("fedinfo", federation.info_feds))

    # Add handler for help command
    app.add_handler(CommandHandler("help", help.help_menu))

    await app.start_polling()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(start_bot())

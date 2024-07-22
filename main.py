import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client, idle
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from modules import federation, help

# Load environment variables from .env file
load_dotenv()

# Get configuration values
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if BOT_TOKEN is loaded correctly
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Please check your .env file.")

# Initialize the Pyrogram Client
app = Client("fedban_bot", bot_token=BOT_TOKEN)

async def start_bot():
    await app.start()
    await federation.init_db(DATABASE_URL)
    print("Bot started successfully!")

    # Add handlers for federation commands
    app.add_handler(MessageHandler(federation.new_fed, command("newfed")))
    app.add_handler(MessageHandler(federation.join_fed, command("joinfed")))
    app.add_handler(MessageHandler(federation.leave_fed, command("leavefed")))
    app.add_handler(MessageHandler(federation.rename_fed, command("renamefed")))
    app.add_handler(MessageHandler(federation.info_feds, command("fedinfo")))

    # Add handler for help command
    app.add_handler(MessageHandler(help.help_menu, command("help")))

    # Register help menu handlers
    help.register_help_handlers(app)

    await idle()  # Keep the bot running

async def main():
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())

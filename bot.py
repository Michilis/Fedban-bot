import os
import logging
from pyrogram import Client, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot
app = Client("fedban_bot", bot_token=os.getenv("BOT_TOKEN"))

# Import all modules
from wbb.modules import admin, karma, fedban
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Fedban Bot is active!")

# Run the bot
app.run()

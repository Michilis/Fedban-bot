from pyrogram import Client
import os

app = Client(
    "fedban_bot",
    bot_token=os.getenv("BOT_TOKEN")
)

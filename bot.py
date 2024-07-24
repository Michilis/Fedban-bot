from pyrogram import Client, filters
from config import BOT_TOKEN
from database.db import create_tables
from handlers.help import register_help_handlers
from handlers.federation import *

app = Client(
    "my_bot",
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await help_menu(client, message)

@app.on_message(filters.command("fedhelp"))
async def help_command(client, message):
    await help_menu(client, message)

create_tables()
register_help_handlers(app)

if __name__ == "__main__":
    app.run()

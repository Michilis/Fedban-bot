import asyncio
from pyrogram import Client, filters
from config import Config
from modules import federation, help

app = Client("fedban_bot", bot_token=Config.BOT_TOKEN)

async def start_bot():
    await app.start()
    await federation.init_db()
    print("Bot started successfully!")

    # Add handlers for federation commands
    app.add_handler(filters.command("newfed"), federation.new_fed)
    app.add_handler(filters.command("joinfed"), federation.join_fed)
    app.add_handler(filters.command("leavefed"), federation.leave_fed)
    app.add_handler(filters.command("renamefed"), federation.rename_fed)

    # Add handler for help command
    app.add_handler(filters.command("help"), help.help_menu)

    # Register help menu handlers
    help.register_help_handlers(app)

    await idle()  # Keep the bot running

async def main():
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())

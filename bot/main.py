import asyncio
from bot.app import app
from bot.db import init_db
from bot.commands import register_command_handlers

async def main():
    await init_db()
    register_command_handlers(app)
    print("Bot is running...")
    await app.start()
    await app.updater.start_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()

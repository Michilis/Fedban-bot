from pyrogram import Client

from config import BOT_TOKEN
from db import init_db

app = Client("fedban_bot", bot_token=BOT_TOKEN)

# Import commands and callbacks to register them
import commands
import callbacks

async def main():
    await init_db()
    await app.start()
    print("Bot is running...")
    await app.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

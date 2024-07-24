from pyrogram import Client
from pyrogram.types import CallbackQuery

@app.on_callback_query(filters.regex(r"rmfed_(.*)"))
async def del_fed_button(client: Client, cb: CallbackQuery):
    # Implement the delete federation confirmation logic here
    pass

@app.on_callback_query(filters.regex(r"trfed_(.*)"))
async def fedtransfer_button(client: Client, cb: CallbackQuery):
    # Implement the federation transfer logic here
    pass

# Add more callback query handlers here

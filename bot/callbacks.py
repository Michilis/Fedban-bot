from pyrogram import Client
from pyrogram.types import CallbackQuery

from db import delete_federation, transfer_owner
from config import SUDOERS

@app.on_callback_query(filters.regex(r"rmfed_(.*)"))
async def del_fed_button(client: Client, cb: CallbackQuery):
    fed_id = cb.data.split("_")[1]
    await delete_federation(fed_id)
    await cb.message.edit_text("Federation deleted.")

@app.on_callback_query(filters.regex(r"trfed_(.*)"))
async def fedtransfer_button(client: Client, cb: CallbackQuery):
    data = cb.data.split("_")[1]
    new_owner_id, fed_id = map(int, data.split("|"))
    await transfer_owner(fed_id, cb.from_user.id, new_owner_id)
    await cb.message.edit_text("Federation ownership transferred.")

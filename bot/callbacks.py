from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from db import delete_federation, transfer_owner, get_fed_info
from utils import create_confirmation_markup
from config import LOG_GROUP_ID, SUDOERS

@app.on_callback_query(filters.regex(r"rmfed_(.*)"))
async def del_fed_button(client: Client, cb: CallbackQuery):
    fed_id = cb.data.split("_")[1]

    if fed_id == "cancel":
        await cb.message.edit_text("Federation deletion cancelled")
        return

    fed_info = await get_fed_info(fed_id)
    if fed_info:
        await delete_federation(fed_id)
        await cb.message.edit_text(
            f"You have removed your Federation! Now all the groups that are connected with `{fed_info['fed_name']}` do not have a Federation.",
            parse_mode="markdown"
        )

@app.on_callback_query(filters.regex(r"trfed_(.*)"))
async def fedtransfer_button(client: Client, cb: CallbackQuery):
    data = cb.data.split("_")[1]

    if data == "cancel":
        return await cb.message.edit_text("Federation transfer cancelled")

    new_owner_id, fed_id = data.split("|")
    new_owner_id = int(new_owner_id)
    fed_id = str(fed_id)

    transferred = await transfer_owner(fed_id, cb.from_user.id, new_owner_id)
    if transferred:
        await cb.message.edit_text(
            "Successfully transferred ownership to new owner."
        )

@app.on_callback_query(filters.regex("fed_(.*)"))
async def fed_owner_help(client: Client, cb: CallbackQuery):
    query = cb.data
    data = query.split("_")[1]
    if data == "owner":
        text = """**👑 Fed Owner Only:**
 • /newfed <fed_name>**:** Creates a Federation, One allowed per user
 • /renamefed <fed_id> <new_fed_name>**:** Renames the fed id to a new name
 • /delfed <fed_id>**:** Delete a Federation, and any information related to it. Will not cancel blocked users
 • /myfeds**:** To list the federations that you have created
 • /fedtransfer <new_owner> <fed_id>**:**To transfer fed ownership to another person
 • /fpromote <user>**:** Assigns the user as a federation admin. Enables all commands for the user under `Fed Admins`
 • /fdemote <user>**:** Drops the User from the admin Federation to a normal User
 • /setfedlog <fed_id>**:** Sets the group as a fed log report base for the federation
 • /unsetfedlog <fed_id>**:** Removed the group as a fed log report base for the federation
 • /fbroadcast **:** Broadcasts a messages to all groups that have joined your fed """
    elif data == "admin":
        text = """**🔱 Fed Admins:**
 • /fban <user> <reason>**:** Fed bans a user
 • /sfban**:** Fban a user without sending notification to chats
 • /unfban <user> <reason>**:** Removes a user from a fed ban
 • /sunfban**:** Unfban a user without sending a notification
 • /fedadmins**:** Show Federation admin
 • /fedchats <Fed_ID>**:** Get all the chats that are connected in the Federation
 • /fbroadcast **:** Broadcasts a messages to all groups that have joined your fed
 """
    else:
        text = """**User Commands:**
• /fedinfo <Fed_ID>: Information about a federation.
• /fedadmins <Fed_ID>: List the admins in a federation.
• /joinfed <Fed_ID>: Join the current chat to a federation. A chat can only join one federation. Chat owners only.
• /leavefed: Leave the current federation. Only chat owners can do this.
• /fedstat: List all the federations that you have been banned in.
• /fedstat <user_ID>: List all the federations that a user has been banned in.
• /fedstat <Fed_ID>: Gives information about your ban in a federation.
• /fedstat <user_ID> <FedID>: Gives information about a user's ban in a federation.
• /chatfed: Information about the federation the current chat is in.
"""
    await cb.message.edit(
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Back", callback_data="help_module(federation)"
                    ),
                ]
            ]
        ),
        parse_mode="markdown",
    )

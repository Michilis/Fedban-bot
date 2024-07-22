import asyncio
import logging
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from wbb import app, SUDOERS
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import (
    add_fedban_user,
    remove_fedban_user,
    is_user_fedbanned,
    get_federations,
    get_federation_info,
    add_group_to_federation,
    remove_group_from_federation,
    create_federation,
    delete_federation,
    transfer_federation_ownership,
)

__MODULE__ = "Fedban"
__HELP__ = """
/newfed <federation_name> - Create a new federation
/delfed <federation_id> - Delete a federation
/fedtransfer <@username> <federation_id> - Transfer federation ownership
/myfeds - List federations created by the user
/renamefed <federation_id> <new_name> - Rename a federation
/addgroup - Add the current group to a federation
/removegroup - Remove the current group from a federation
/fban <user_id> - Ban a user in all federated groups
/unfban <user_id> - Unban a user in all federated groups
/fedinfo <federation_id> - Get information about a federation
/fedadmins <federation_id> - List federation admins
"""

# Set up logging
logger = logging.getLogger(__name__)

# Create a new federation
@app.on_message(filters.command("newfed") & filters.private & ~filters.edited)
@capture_err
async def new_fed(client, message):
    user = message.from_user
    if len(message.command) < 2:
        return await message.reply_text("Please specify the name of the federation!")
    
    federation_name = message.text.split(None, 1)[1]
    federation_id = await create_federation(user.id, federation_name)
    await message.reply_text(
        f"Federation created successfully!\nName: `{federation_name}`\nID: `{federation_id}`\n\n"
        f"Use `/joinfed {federation_id}` in a group to add it to this federation."
    )

# Delete a federation
@app.on_message(filters.command("delfed") & filters.private & ~filters.edited)
@capture_err
async def del_fed(client, message):
    user = message.from_user
    if len(message.command) < 2:
        return await message.reply_text("Please specify the federation ID!")

    federation_id = message.command[1]
    federation_info = await get_federation_info(federation_id)
    
    if federation_info["owner_id"] != user.id and user.id not in SUDOERS:
        return await message.reply_text("Only the federation owner can delete it.")
    
    await delete_federation(federation_id)
    await message.reply_text(f"Federation `{federation_info['name']}` deleted successfully.")

# Transfer federation ownership
@app.on_message(filters.command("fedtransfer") & filters.private & ~filters.edited)
@capture_err
async def fed_transfer(client, message):
    user = message.from_user
    if len(message.command) < 3:
        return await message.reply_text("Usage: /fedtransfer <@username> <federation_id>")
    
    new_owner_username, federation_id = message.command[1], message.command[2]
    new_owner_id = await app.get_users(new_owner_username)
    
    federation_info = await get_federation_info(federation_id)
    if federation_info["owner_id"] != user.id and user.id not in SUDOERS:
        return await message.reply_text("Only the federation owner can transfer ownership.")
    
    await transfer_federation_ownership(federation_id, new_owner_id.id)
    await message.reply_text(f"Federation ownership transferred to {new_owner_username}.")

# List federations created by the user
@app.on_message(filters.command("myfeds") & filters.private & ~filters.edited)
@capture_err
async def my_feds(client, message):
    user = message.from_user
    federations = await get_federations(user.id)
    
    if not federations:
        return await message.reply_text("You haven't created any federations.")
    
    response = "Federations you have created:\n\n"
    for federation in federations:
        response += f"Name: `{federation['name']}`\nID: `{federation['id']}`\n\n"
    
    await message.reply_text(response)

# Rename a federation
@app.on_message(filters.command("renamefed") & filters.private & ~filters.edited)
@capture_err
async def rename_fed(client, message):
    user = message.from_user
    if len(message.command) < 3:
        return await message.reply_text("Usage: /renamefed <federation_id> <new_name>")
    
    federation_id, new_name = message.command[1], message.command[2]
    federation_info = await get_federation_info(federation_id)
    
    if federation_info["owner_id"] != user.id and user.id not in SUDOERS:
        return await message.reply_text("Only the federation owner can rename it.")
    
    await update_federation_name(federation_id, new_name)
    await message.reply_text(f"Federation renamed to `{new_name}`.")

# Add the current group to a federation
@app.on_message(filters.command("addgroup") & ~filters.private & ~filters.edited)
@capture_err
async def add_group(client, message):
    user = message.from_user
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        return await message.reply_text("Usage: /addgroup <federation_id>")
    
    federation_id = message.command[1]
    federation_info = await get_federation_info(federation_id)
    
    if federation_info["owner_id"] != user.id and user.id not in SUDOERS:
        return await message.reply_text("Only the federation owner can add groups to it.")
    
    await add_group_to_federation(federation_id, chat_id)
    await message.reply_text(f"This group has been added to the federation `{federation_info['name']}`.")

# Remove the current group from a federation
@app.on_message(filters.command("removegroup") & ~filters.private & ~filters.edited)
@capture_err
async def remove_group(client, message):
    user = message.from_user
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        return await message.reply_text("Usage: /removegroup <federation_id>")
    
    federation_id = message.command[1]
    federation_info = await get_federation_info(federation_id)
    
    if federation_info["owner_id"] != user.id and user.id not in SUDOERS:
        return await message.reply_text("Only the federation owner can remove groups from it.")
    
    await remove_group_from_federation(federation_id, chat_id)
    await message.reply_text(f"This group has been removed from the federation `{federation_info['name']}`.")

# Ban a user in all federated groups
@app.on_message(filters.command("fban") & ~filters.private & ~filters.edited)
@capture_err
async def fed_ban(client, message):
    user = message.from_user
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fban <user_id>")
    
    user_id = int(message.command[1])
    federations = await get_federations(user.id)
    
    for federation in federations:
        groups = await get_groups_in_federation(federation["id"])
        for group in groups:
            await app.ban_chat_member(group, user_id)
            await add_fedban_user(federation["id"], user_id)
    
    await message.reply_text(f"User {user_id} has been banned in all federated groups.")

# Unban a user in all federated groups
@app.on_message(filters.command("unfban") & ~filters.private & ~filters.edited)
@capture_err
async def fed_unban(client, message):
    user = message.from_user
    if len(message.command) < 2:
        return await message.reply_text("Usage: /unfban <user_id>")
    
    user_id = int(message.command[1])
    federations = await get_federations(user.id)
    
    for federation in federations:
        groups = await get_groups_in_federation(federation["id"])
        for group in groups:
            await app.unban_chat_member(group, user_id)
            await remove_fedban_user(federation["id"], user_id)
    
    await message.reply_text(f"User {user_id} has been unbanned in all federated groups.")

# Get information about a federation
@app.on_message(filters.command("fedinfo") & ~filters.private & ~filters.edited)
@capture_err
async def fed_info(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fedinfo <federation_id>")
    
    federation_id = message.command[1]
    federation_info = await get_federation_info(federation_id)
    
    if not federation_info:
        return await message.reply_text("Federation not found.")
    
    response = (
        f"**Federation Information**\n"
        f"Name: `{federation_info['name']}`\n"
        f"ID: `{federation_id}`\n"
        f"Owner: `{federation_info['owner_id']}`\n"
        f"Groups: {len(federation_info['groups'])}\n"
    )
    await message.reply_text(response)

# List federation admins
@app.on_message(filters.command("fedadmins") & ~filters.private & ~filters.edited)
@capture_err
async def fed_admins(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fedadmins <federation_id>")
    
    federation_id = message.command[1]
    federation_info = await get_federation_info(federation_id)
    
    if not federation_info:
        return await message.reply_text("Federation not found.")
    
    response = "Federation Admins:\n\n"
    response += f"Owner: `{federation_info['owner_id']}`\n"
    for admin in federation_info['admins']:
        response += f"Admin: `{admin}`\n"
    
    await message.reply_text(response)

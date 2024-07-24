from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from db import (
    create_federation, delete_federation, get_fed_info, get_feds_by_owner,
    add_fed_admin, remove_fed_admin, add_banned_user, remove_banned_user, set_log_chat,
    get_fed_id, is_user_fed_owner, check_banned_user, chat_join_fed, chat_leave_fed,
    search_fed_by_id, is_group_admin, chat_id_and_names_in_fed,
    transfer_owner, get_user_fstatus
)
from utils import generate_fed_id, create_confirmation_markup, extract_user_and_reason
from config import LOG_GROUP_ID, SUDOERS
from app import app  # Import the app instance

@app.on_message(filters.command("newfed"))
async def new_fed(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Federations can only be created by privately messaging me.")
    if len(message.command) < 2:
        return await message.reply_text("Please write the name of the federation!")
    fed_name = message.text.split(None, 1)[1]
    fed_id = await generate_fed_id(message.from_user.id)
    await create_federation(fed_id, fed_name, message.from_user.id, message.from_user.mention, LOG_GROUP_ID)
    await message.reply_text(f"New federation created!\nName: {fed_name}\nID: {fed_id}")

@app.on_message(filters.command("delfed"))
async def del_fed(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Federations can only be deleted by privately messaging me.")
    if len(message.command) < 2:
        return await message.reply_text("Please provide the federation ID.")
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text("Only federation owners can delete federations.")
    await delete_federation(fed_id)
    await message.reply_text(f"Federation {fed_info['fed_name']} deleted.")

@app.on_message(filters.command("fedtransfer"))
async def fed_transfer(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Federations can only be transferred by privately messaging me.")
    if len(message.command) < 3:
        return await message.reply_text("Usage: /fedtransfer @username fed_id")
    user_id, fed_id = extract_user_and_reason(message)
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text("Only federation owners can transfer federations.")
    await add_fed_admin(fed_id, user_id)
    await message.reply_text(f"Federation {fed_info['fed_name']} transferred to {user_id}.")

@app.on_message(filters.command("myfeds"))
async def my_feds(client: Client, message: Message):
    feds = await get_feds_by_owner(message.from_user.id)
    if not feds:
        return await message.reply_text("You haven't created any federations.")
    fed_list = "\n".join([f"Name: {fed['fed_name']} - ID: {fed['fed_id']}" for fed in feds])
    await message.reply_text(f"Your federations:\n{fed_list}")

@app.on_message(filters.command("renamefed"))
async def rename_fed(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Usage: /renamefed fed_id new_name")
    fed_id, new_name = message.command[1], message.command[2]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text("Only federation owners can rename federations.")
    conn = await get_conn()
    await conn.execute('UPDATE federations SET fed_name = $1 WHERE fed_id = $2', new_name, fed_id)
    await conn.close()
    await message.reply_text(f"Federation renamed to {new_name}.")

@app.on_message(filters.command(["setfedlog", "unsetfedlog"]))
async def set_unset_fed_log(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        if len(message.command) < 3:
            return await message.reply_text(f"Usage:\n\n /{message.command[0]} [channel_id] [fed_id].")
        chat_id = message.command[1]
        fed_id = message.command[2]
    else:
        if len(message.command) < 2:
            return await message.reply_text("Please provide the federation ID.")
        chat_id = message.chat.id
        fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text("Only federation owners can set/unset log channels.")
    log_group_id = LOG_GROUP_ID if "unset" in message.command[0] else chat_id
    await set_log_chat(fed_id, log_group_id)
    await message.reply_text("Log channel set." if "set" in message.command[0] else "Log channel unset.")

@app.on_message(filters.command("chatfed"))
async def chat_fed(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text("This group is not in any federation.")
    fed_info = await get_fed_info(fed_id)
    await message.reply_text(f"This group is part of the federation:\nName: {fed_info['fed_name']}\nID: {fed_id}")

@app.on_message(filters.command("joinfed"))
async def join_fed(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    if len(message.command) < 2:
        return await message.reply_text("Please provide the federation ID.")
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    if not await is_group_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins can join federations.")
    await chat_join_fed(fed_id, message.chat.title, message.chat.id)
    await message.reply_text(f"This group has joined the federation: {fed_info['fed_name']}.")

@app.on_message(filters.command("leavefed"))
async def leave_fed(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text("This group is not in any federation.")
    fed_info = await get_fed_info(fed_id)
    if not await is_group_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins can leave federations.")
    await chat_leave_fed(message.chat.id)
    await message.reply_text(f"This group has left the federation: {fed_info['fed_name']}.")

@app.on_message(filters.command("fedchats"))
async def fed_chats(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Fedchats can only be checked by privately messaging me.")
    if len(message.command) < 2:
        return await message.reply_text("Please provide the federation ID.")
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    if message.from_user.id not in fed_info["fadmins"] + [fed_info["owner_id"]] + SUDOERS:
        return await message.reply_text("You need to be a Fed Admin to use this command.")
    chat_ids, chat_names = await chat_id_and_names_in_fed(fed_id)
    await message.reply_text(f"Chats in the federation {fed_info['fed_name']}:\n" + "\n".join([f"{chat_name} (`{chat_id}`)" for chat_id, chat_name in zip(chat_ids, chat_names)]))

@app.on_message(filters.command("fedinfo"))
async def fed_info(client: Client, message: Message):
    if len(message.command) < 2:
        fed_id = await get_fed_id(message.chat.id)
        if not fed_id:
            return await message.reply_text("Please provide the federation ID.")
    else:
        fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    await message.reply_text(
        f"**Federation Information:**\n"
        f"Name: {fed_info['fed_name']}\n"
        f"Owner: {fed_info['owner_mention']}\n"
        f"Admins: {len(fed_info['fadmins'])}\n"
        f"Banned Users: {len(fed_info['banned_users'])}\n"
        f"Chats: {len(fed_info['chat_ids'])}"
    )

@app.on_message(filters.command("fedadmins"))
async def fed_admins(client: Client, message: Message):
    if len(message.command) < 2:
        fed_id = await get_fed_id(message.chat.id)
        if not fed_id:
            return await message.reply_text("Please provide the federation ID.")
    else:
        fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("This federation does not exist.")
    admin_ids = fed_info["fadmins"]
    admins = [await client.get_users(admin_id) for admin_id in admin_ids]
    await message.reply_text(
        f"**Federation Admins:**\nOwner: {fed_info['owner_mention']}\n" +
        "\n".join([f"{admin.mention} ({admin.id})" for admin in admins])
    )

@app.on_message(filters.command("fpromote"))
async def fpromote(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text("This group is not in any federation.")
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text("Only federation owners can promote admins.")
    user_id, _ = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("Please specify a user to promote.")
    await add_fed_admin(fed_id, user_id)
    await message.reply_text("User promoted to federation admin.")

@app.on_message(filters.command("fdemote"))
async def fdemote(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text("This group is not in any federation.")
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text("Only federation owners can demote admins.")
    user_id, _ = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("Please specify a user to demote.")
    await remove_fed_admin(fed_id, user_id)
    await message.reply_text("User demoted from federation admin.")

@app.on_message(filters.command(["fban", "sfban"]))
async def fban_user(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text("This group is not in any federation.")
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text("Only federation owners and admins can ban users.")
    user_id, reason = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("Please specify a user to ban.")
    await add_banned_user(fed_id, user_id, reason)
    await message.reply_text("User has been banned in the federation.")

@app.on_message(filters.command(["unfban", "sunfban"]))
async def funban_user(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text("This group is not in any federation.")
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text("Only federation owners and admins can unban users.")
    user_id, reason = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("Please specify a user to unban.")
    await remove_banned_user(fed_id, user_id)
    await message.reply_text("User has been unbanned in the federation.")

@app.on_message(filters.command("fedstat"))
async def fed_stat(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Federation Ban status can only be checked by privately messaging me.")
    if len(message.command) < 2:
        user_id = message.from_user.id
    else:
        user_id = int(message.command[1])
    status = await get_user_fstatus(user_id)
    user = await client.get_users(user_id)
    if status:
        response_text = "\n\n".join(
            [f"{i + 1}) **Fed Name:** {fed['fed_name']}\n  **Fed Id:** `{fed['fed_id']}`" for i, fed in enumerate(status)]
        )
        await message.reply_text(f"**Here is the list of federations that {user.mention} were banned in:**\n\n{response_text}")
    else:
        return await message.reply_text(f"**{user.mention} is not banned in any federations.**")

@app.on_message(filters.command("fbroadcast"))
async def fbroadcast_message(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups.")
    if not message.reply_to_message:
        return await message.reply_text("You need to reply to a message to broadcast it.")
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text("This group is not in any federation.")
    fed_info = await get_fed_info(fed_id)
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text("Only federation owners and admins can broadcast messages.")
    chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(f"Broadcast in progress, will take {len(chats)} seconds.")
    for chat_id in chats:
        try:
            await message.reply_to_message.copy(chat_id)
            await asyncio.sleep(0.1)
        except Exception:
            pass
    await m.edit(f"Broadcasted message in {len(chats)} chats.")

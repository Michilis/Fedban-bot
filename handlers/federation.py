import asyncio
import uuid
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType, ParseMode
from pyrogram.errors import FloodWait, PeerIdInvalid, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db import fetch_one, fetch_all, execute_query

SUPPORT_CHAT = "@YourSupportChat"  # Replace with your support chat

async def extract_user_and_reason(message):
    user_id = None
    reason = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    else:
        if len(message.command) > 1:
            args = message.text.split(None, 2)
            user_id = args[1]
            reason = args[2] if len(args) > 2 else None
    return user_id, reason

async def extract_user(message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        if len(message.command) > 1:
            user_id = message.text.split(None, 1)[1]
    return user_id

async def new_fed(client, message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Federations can only be created by privately messaging me.")

    if len(message.command) < 2:
        return await message.reply_text("Please write the name of the federation!")

    fed_name = message.text.split(None, 1)[1]
    fed_id = f"{user.id}:{uuid.uuid4()}"
    execute_query('''
        INSERT INTO federations (fed_id, fed_name, owner_id, fadmins, banned_users, chat_ids)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (fed_id, fed_name, user.id, [], [], []))

    await message.reply_text(
        f"**You have succeeded in creating a new federation!**\n"
        f"Name: {fed_name}\nID: {fed_id}\n\n"
        f"Use the command below to join the federation:\n"
        f"/joinfed {fed_id}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def del_fed(client, message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Federations can only be deleted by privately messaging me.")

    args = message.text.split(" ", 1)
    if len(args) > 1:
        fed_id = args[1].strip()
        fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
        if not fed_info:
            return await message.reply_text("This federation does not exist.")
        
        if fed_info['owner_id'] == user.id:
            execute_query('DELETE FROM federations WHERE fed_id = %s', (fed_id,))
            return await message.reply_text(f"Federation '{fed_info['fed_name']}' has been deleted.")
        else:
            return await message.reply_text("Only federation owners can delete the federation!")
    else:
        return await message.reply_text("Please provide the federation ID to delete.")

async def fedtransfer(client, message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("Federations can only be transferred by privately messaging me.")

    if len(message.command) < 3:
        return await message.reply_text("Usage: /fedtransfer <new_owner_id> <fed_id>")
    
    new_owner_id = int(message.command[1])
    fed_id = message.command[2]
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s AND owner_id = %s', (fed_id, user.id))
    if not fed_info:
        return await message.reply_text("Federation not found or you are not the owner.")

    execute_query('UPDATE federations SET owner_id = %s WHERE fed_id = %s', (new_owner_id, fed_id))
    await message.reply_text(f"Federation '{fed_info['fed_name']}' has been transferred to {new_owner_id}.")

async def myfeds(client, message):
    user = message.from_user
    feds = fetch_all('SELECT * FROM federations WHERE owner_id = %s', (user.id,))
    
    if not feds:
        return await message.reply_text("You haven't created any federations.")
    
    response_text = "\n\n".join([f"Name: {fed['fed_name']}\nID: {fed['fed_id']}" for fed in feds])
    await message.reply_text(f"**Here are the federations you have created:**\n\n{response_text}")

async def rename_fed(client, message):
    user = message.from_user
    if len(message.command) < 3:
        return await message.reply_text("Usage: /renamefed <fed_id> <new_name>")
    
    fed_id = message.command[1]
    new_name = message.command[2]
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s AND owner_id = %s', (fed_id, user.id))
    if not fed_info:
        return await message.reply_text("Federation not found or you are not the owner.")
    
    execute_query('UPDATE federations SET fed_name = %s WHERE fed_id = %s', (new_name, fed_id))
    await message.reply_text(f"Federation '{fed_id}' has been renamed to {new_name}.")

async def fed_log(client, message):
    user = message.from_user
    if len(message.command) < 3:
        return await message.reply_text(f"Usage: /{message.command[0]} <channel_id> <fed_id>")
    
    channel_id = message.command[1]
    fed_id = message.command[2]
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s AND owner_id = %s', (fed_id, user.id))
    if not fed_info:
        return await message.reply_text("Federation not found or you are not the owner.")
    
    if message.command[0] == "setfedlog":
        execute_query('UPDATE federations SET log_group_id = %s WHERE fed_id = %s', (channel_id, fed_id))
        await message.reply_text(f"Log group has been set for federation '{fed_info['fed_name']}' to {channel_id}.")
    else:
        execute_query('UPDATE federations SET log_group_id = NULL WHERE fed_id = %s', (fed_id,))
        await message.reply_text(f"Log group has been unset for federation '{fed_info['fed_name']}'.")

async def fed_chat(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")

    fed_id = fetch_one('SELECT fed_id FROM federations WHERE %s = ANY(chat_ids)', (message.chat.id,))
    if not fed_id:
        return await message.reply_text("This group is not part of any federation!")
    
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    await message.reply_text(f"This group is part of the following federation:\n\nName: {fed_info['fed_name']}\nID: {fed_info['fed_id']}", parse_mode=ParseMode.HTML)

async def join_fed(client, message):
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /joinfed <fed_id>")
    
    fed_id = message.command[1]
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if not fed_info:
        return await message.reply_text("Federation not found.")

    execute_query('UPDATE federations SET chat_ids = array_append(chat_ids, %s) WHERE fed_id = %s', (message.chat.id, fed_id))
    await message.reply_text(f"This group has joined the federation: {fed_info['fed_name']}!")

async def leave_fed(client, message):
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")

    fed_id = fetch_one('SELECT fed_id FROM federations WHERE %s = ANY(chat_ids)', (message.chat.id,))
    if not fed_id:
        return await message.reply_text("This group is not part of any federation!")
    
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    execute_query('UPDATE federations SET chat_ids = array_remove(chat_ids, %s) WHERE fed_id = %s', (message.chat.id, fed_id))
    await message.reply_text(f"This group has left the federation: {fed_info['fed_name']}!")

async def fed_chats(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fedchats <fed_id>")
    
    fed_id = message.command[1]
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if not fed_info:
        return await message.reply_text("Federation not found.")

    chat_ids = fed_info['chat_ids']
    chat_names = [await client.get_chat(chat_id).title for chat_id in chat_ids]
    response_text = "\n".join([f"{chat_name} [{chat_id}]" for chat_name, chat_id in zip(chat_names, chat_ids)])
    await message.reply_text(f"**Here are the chats connected to this federation:**\n\n{response_text}")

async def fed_info(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fedinfo <fed_id>")
    
    fed_id = message.command[1]
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if not fed_info:
        return await message.reply_text("Federation not found.")

    response_text = (
        f"**Federation Information:**\n\n"
        f"**Name:** {fed_info['fed_name']}\n"
        f"**ID:** {fed_info['fed_id']}\n"
        f"**Owner ID:** {fed_info['owner_id']}\n"
        f"**Number of Admins:** {len(fed_info['fadmins'])}\n"
        f"**Number of Banned Users:** {len(fed_info['banned_users'])}\n"
        f"**Number of Chats:** {len(fed_info['chat_ids'])}"
    )
    await message.reply_text(response_text)

async def get_all_fadmins_mentions(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fedadmins <fed_id>")
    
    fed_id = message.command[1]
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if not fed_info:
        return await message.reply_text("Federation not found.")

    fadmin_ids = fed_info['fadmins']
    user_mentions = [f"- {await client.get_users(fadmin_id).mention}" for fadmin_id in fadmin_ids]
    response_text = f"**Federation Admins:**\n\n" + "\n".join(user_mentions)
    await message.reply_text(response_text)

async def fpromote(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")
    
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fpromote <user_id>")
    
    user_id = int(message.command[1])
    fed_id = fetch_one('SELECT fed_id FROM federations WHERE %s = ANY(chat_ids)', (message.chat.id,))
    if not fed_id:
        return await message.reply_text("This group is not part of any federation!")
    
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if user_id in fed_info['fadmins']:
        return await message.reply_text("This user is already a federation admin!")
    
    execute_query('UPDATE federations SET fadmins = array_append(fadmins, %s) WHERE fed_id = %s', (user_id, fed_id))
    await message.reply_text(f"User {user_id} has been promoted to federation admin!")

async def fdemote(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")
    
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fdemote <user_id>")
    
    user_id = int(message.command[1])
    fed_id = fetch_one('SELECT fed_id FROM federations WHERE %s = ANY(chat_ids)', (message.chat.id,))
    if not fed_id:
        return await message.reply_text("This group is not part of any federation!")
    
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if user_id not in fed_info['fadmins']:
        return await message.reply_text("This user is not a federation admin!")
    
    execute_query('UPDATE federations SET fadmins = array_remove(fadmins, %s) WHERE fed_id = %s', (user_id, fed_id))
    await message.reply_text(f"User {user_id} has been demoted from federation admin!")

async def fban_user(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")

    fed_id = fetch_one('SELECT fed_id FROM federations WHERE %s = ANY(chat_ids)', (message.chat.id,))
    if not fed_id:
        return await message.reply_text("This group is not part of any federation!")

    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("Usage: /fban <user_id> <reason>")
    
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if user_id in fed_info['banned_users']:
        return await message.reply_text("This user is already banned from the federation!")

    execute_query('UPDATE federations SET banned_users = array_append(banned_users, %s) WHERE fed_id = %s', (user_id, fed_id))
    await message.reply_text(f"User {user_id} has been banned from the federation!")

async def funban_user(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")

    fed_id = fetch_one('SELECT fed_id FROM federations WHERE %s = ANY(chat_ids)', (message.chat.id,))
    if not fed_id:
        return await message.reply_text("This group is not part of any federation!")

    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("Usage: /unfban <user_id> <reason>")
    
    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    if user_id not in fed_info['banned_users']:
        return await message.reply_text("This user is not banned from the federation!")

    execute_query('UPDATE federations SET banned_users = array_remove(banned_users, %s) WHERE fed_id = %s', (user_id, fed_id))
    await message.reply_text(f"User {user_id} has been unbanned from the federation!")

async def status(message, user_id):
    status = fetch_all('SELECT * FROM federations WHERE %s = ANY(banned_users)', (user_id,))
    if status:
        response_text = "\n\n".join([f"Name: {fed['fed_name']}\nID: {fed['fed_id']}" for fed in status])
        await message.reply_text(f"Here is the list of federations that user {user_id} is banned in:\n\n{response_text}")
    else:
        await message.reply_text(f"User {user_id} is not banned in any federations.")

async def fedstat(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /fedstat <user_id>")
    
    user_id = int(message.command[1])
    await status(message, user_id)

async def fbroadcast_message(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command is specific to groups, not private messages!")

    fed_id = fetch_one('SELECT fed_id FROM federations WHERE %s = ANY(chat_ids)', (message.chat.id,))
    if not fed_id:
        return await message.reply_text("This group is not part of any federation!")

    if not message.reply_to_message:
        return await message.reply_text("You need to reply to a message to broadcast it.")

    fed_info = fetch_one('SELECT * FROM federations WHERE fed_id = %s', (fed_id,))
    chat_ids = fed_info['chat_ids']
    sleep_time = 0.1
    sent = 0
    for chat_id in chat_ids:
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
            await asyncio.sleep(sleep_time)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception:
            pass

    await message.reply_text(f"Broadcasted message to {sent} chats.")

def register_federation_handlers(app):
    app.add_handler(filters.command("newfed")(new_fed))
    app.add_handler(filters.command("delfed")(del_fed))
    app.add_handler(filters.command("fedtransfer")(fedtransfer))
    app.add_handler(filters.command("myfeds")(myfeds))
    app.add_handler(filters.command("renamefed")(rename_fed))
    app.add_handler(filters.command(["setfedlog", "unsetfedlog"])(fed_log))
    app.add_handler(filters.command("chatfed")(fed_chat))
    app.add_handler(filters.command("joinfed")(join_fed))
    app.add_handler(filters.command("leavefed")(leave_fed))
    app.add_handler(filters.command("fedchats")(fed_chats))
    app.add_handler(filters.command("fedinfo")(fed_info))
    app.add_handler(filters.command("fedadmins")(get_all_fadmins_mentions))
    app.add_handler(filters.command("fpromote")(fpromote))
    app.add_handler(filters.command("fdemote")(fdemote))
    app.add_handler(filters.command(["fban", "sfban"])(fban_user))
    app.add_handler(filters.command(["unfban", "sunfban"])(funban_user))
    app.add_handler(filters.command("fedstat")(fedstat))
    app.add_handler(filters.command("fbroadcast")(fbroadcast_message))

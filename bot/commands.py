from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.app import app  # Import the app instance
from bot.db import (
    create_federation, delete_federation, get_fed_info, get_feds_by_owner,
    add_fed_admin, remove_fed_admin, add_banned_user, remove_banned_user, set_log_chat,
    get_fed_id, is_user_fed_owner, check_banned_user, chat_join_fed, chat_leave_fed,
    search_fed_by_id, is_group_admin, chat_id_and_names_in_fed,
    transfer_owner, get_user_fstatus
)
from bot.utils import generate_fed_id, create_confirmation_markup, extract_user_and_reason
from bot.messages import MESSAGES
from config import LOG_GROUP_ID, SUDOERS

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(MESSAGES["start_message"])

@app.on_message(filters.command("fedhelp"))
async def fedhelp(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin")],
            [InlineKeyboardButton("Federation Owner Commands", callback_data="fed_owner")],
            [InlineKeyboardButton("User Commands", callback_data="user")],
        ]
    )
    await message.reply(MESSAGES["help_menu"], reply_markup=keyboard)

@app.on_message(filters.command("newfed"))
async def new_fed(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["create_fed_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_name"])
    fed_name = message.text.split(None, 1)[1]
    fed_id = await generate_fed_id(message.from_user.id)
    await create_federation(fed_id, fed_name, message.from_user.id, message.from_user.mention, LOG_GROUP_ID)
    await message.reply_text(MESSAGES["new_fed_created"].format(fed_name=fed_name, fed_id=fed_id))

@app.on_message(filters.command("delfed"))
async def del_fed(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["delete_fed_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text(MESSAGES["only_fed_owners_can_delete"])
    await delete_federation(fed_id)
    await message.reply_text(MESSAGES["fed_deleted"].format(fed_name=fed_info['fed_name']))

@app.on_message(filters.command("fedtransfer"))
async def fed_transfer(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["transfer_fed_private"])
    if len(message.command) < 3:
        return await message.reply_text(MESSAGES["transfer_fed_usage"])
    user_id, fed_id = extract_user_and_reason(message)
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text(MESSAGES["only_fed_owners_can_transfer"])
    await add_fed_admin(fed_id, user_id)
    await message.reply_text(MESSAGES["fed_transferred"].format(fed_name=fed_info['fed_name'], user_id=user_id))

@app.on_message(filters.command("myfeds"))
async def my_feds(client: Client, message: Message):
    feds = await get_feds_by_owner(message.from_user.id)
    if not feds:
        return await message.reply_text(MESSAGES["no_federations_created"])
    fed_list = "\n".join([f"Name: {fed['fed_name']} - ID: {fed['fed_id']}" for fed in feds])
    await message.reply_text(MESSAGES["your_federations"].format(fed_list=fed_list))

@app.on_message(filters.command("renamefed"))
async def rename_fed(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text(MESSAGES["rename_fed_usage"])
    fed_id, new_name = message.command[1], message.command[2]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text(MESSAGES["only_fed_owners_can_rename"])
    conn = await get_conn()
    await conn.execute('UPDATE federations SET fed_name = $1 WHERE fed_id = $2', new_name, fed_id)
    await conn.close()
    await message.reply_text(MESSAGES["fed_renamed"].format(new_name=new_name))

@app.on_message(filters.command(["setfedlog", "unsetfedlog"]))
async def set_unset_fed_log(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        if len(message.command) < 3:
            return await message.reply_text(MESSAGES["set_unset_fed_log_private"].format(command=message.command[0]))
        chat_id = message.command[1]
        fed_id = message.command[2]
    else:
        if len(message.command) < 2:
            return await message.reply_text(MESSAGES["provide_fed_id"])
        chat_id = message.chat.id
        fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != message.from_user.id:
        return await message.reply_text(MESSAGES["only_fed_owners_can_set_unset_log"])
    log_group_id = LOG_GROUP_ID if "unset" in message.command[0] else chat_id
    await set_log_chat(fed_id, log_group_id)
    await message.reply_text(MESSAGES["log_channel_set"] if "set" in message.command[0] else MESSAGES["log_channel_unset"])

@app.on_message(filters.command("chatfed"))
async def chat_fed(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["chat_fed_private"])
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = await get_fed_info(fed_id)
    await message.reply_text(MESSAGES["group_in_federation"].format(fed_name=fed_info['fed_name'], fed_id=fed_id))

@app.on_message(filters.command("joinfed"))
async def join_fed(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["join_fed_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id_join"])
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if not await is_group_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(MESSAGES["only_group_admins_can_join"])
    await chat_join_fed(fed_id, message.chat.title, message.chat.id)
    await message.reply_text(MESSAGES["group_joined_federation"].format(fed_name=fed_info['fed_name']))

@app.on_message(filters.command("leavefed"))
async def leave_fed(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["leave_fed_private"])
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = await get_fed_info(fed_id)
    if not await is_group_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(MESSAGES["only_group_admins_can_leave"])
    await chat_leave_fed(message.chat.id)
    await message.reply_text(MESSAGES["group_left_federation"].format(fed_name=fed_info['fed_name']))

@app.on_message(filters.command("fedchats"))
async def fed_chats(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fedchats_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id_fedchats"])
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if message.from_user.id not in fed_info["fadmins"] + [fed_info["owner_id"]] + SUDOERS:
        return await message.reply_text(MESSAGES["only_fed_admins_can_check_fedchats"])
    chat_ids, chat_names = await chat_id_and_names_in_fed(fed_id)
    chat_list = "\n".join([f"{chat_name} (`{chat_id}`)" for chat_id, chat_name in zip(chat_ids, chat_names)])
    await message.reply_text(MESSAGES["fed_chats_list"].format(fed_name=fed_info['fed_name'], chat_list=chat_list))

@app.on_message(filters.command("fedinfo"))
async def fed_info(client: Client, message: Message):
    if len(message.command) < 2:
        fed_id = await get_fed_id(message.chat.id)
        if not fed_id:
            return await message.reply_text(MESSAGES["provide_fed_id"])
    else:
        fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    await message.reply_text(
        MESSAGES["fed_info_list"].format(
            fed_name=fed_info['fed_name'],
            owner_mention=fed_info['owner_mention'],
            admins=len(fed_info['fadmins']),
            banned_users=len(fed_info['banned_users']),
            chats=len(fed_info['chat_ids'])
        )
    )

@app.on_message(filters.command("fedadmins"))
async def fed_admins(client: Client, message: Message):
    if len(message.command) < 2:
        fed_id = await get_fed_id(message.chat.id)
        if not fed_id:
            return await message.reply_text(MESSAGES["provide_fed_id"])
    else:
        fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    admin_ids = fed_info["fadmins"]
    admins = [await client.get_users(admin_id) for admin_id in admin_ids]
    admins_list = "\n".join([f"{admin.mention} ({admin.id})" for admin in admins])
    await message.reply_text(MESSAGES["fed_admins_list"].format(owner_mention=fed_info['owner_mention'], admins_list=admins_list))

@app.on_message(filters.command("fpromote"))
async def fpromote(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fpromote_private"])
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text(MESSAGES["only_fed_owners_can_promote"])
    user_id, _ = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    await add_fed_admin(fed_id, user_id)
    await message.reply_text(MESSAGES["user_promoted"])

@app.on_message(filters.command("fdemote"))
async def fdemote(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fdemote_private"])
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text(MESSAGES["only_fed_owners_can_demote"])
    user_id, _ = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    await remove_fed_admin(fed_id, user_id)
    await message.reply_text(MESSAGES["user_demoted"])

@app.on_message(filters.command(["fban", "sfban"]))
async def fban_user(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fban_private"])
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text(MESSAGES["only_fed_admins_can_ban"])
    user_id, reason = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    await add_banned_user(fed_id, user_id, reason)
    await message.reply_text(MESSAGES["user_banned"])

@app.on_message(filters.command(["unfban", "sunfban"]))
async def funban_user(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["unfban_private"])
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text(MESSAGES["only_fed_admins_can_unban"])
    user_id, reason = extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    await remove_banned_user(fed_id, user_id)
    await message.reply_text(MESSAGES["user_unbanned"])

@app.on_message(filters.command("fedstat"))
async def fed_stat(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fedstat_private"])
    if len(message.command) < 2:
        user_id = message.from_user.id
    else:
        user_id = int(message.command[1])
    status = await get_user_fstatus(user_id)
    user = await client.get_users(user_id)
    if status:
        status_list = "\n\n".join(
            [f"{i + 1}) **Fed Name:** {fed['fed_name']}\n  **Fed Id:** `{fed['fed_id']}`" for i, fed in enumerate(status)]
        )
        await message.reply_text(MESSAGES["user_fed_status"].format(user=user.mention, status_list=status_list))
    else:
        return await message.reply_text(MESSAGES["user_not_banned"].format(user=user.mention))

@app.on_message(filters.command("fbroadcast"))
async def fbroadcast_message(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fbroadcast_private"])
    if not message.reply_to_message:
        return await message.reply_text(MESSAGES["reply_to_broadcast"])
    fed_id = await get_fed_id(message.chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = await get_fed_info(fed_id)
    if not await is_user_fed_owner(fed_id, message.from_user.id):
        return await message.reply_text(MESSAGES["only_fed_admins_can_broadcast"])
    chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(MESSAGES["broadcast_in_progress"].format(seconds=len(chats)))
    for chat_id in chats:
        try:
            await message.reply_to_message.copy(chat_id)
            await asyncio.sleep(0.1)
        except Exception:
            pass
    await m.edit(MESSAGES["broadcast_done"].format(count=len(chats)))

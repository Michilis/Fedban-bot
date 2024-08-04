import asyncio
import uuid
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait, PeerIdInvalid, ChatAdminRequired
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.app import app  # Import the app instance
from bot.db import (
    create_federation, delete_federation, get_fed_info, get_feds_by_owner,
    add_fed_admin, remove_fed_admin, add_banned_user, remove_banned_user, set_log_chat,
    get_fed_id, is_user_fed_owner, check_banned_user, chat_join_fed, chat_leave_fed,
    search_fed_by_id, is_group_admin, chat_id_and_names_in_fed,
    transfer_owner, get_user_fstatus
)
from bot.utils import generate_fed_id, create_confirmation_markup, extract_user_and_reason, extract_user
from bot.messages import MESSAGES
from config import LOG_GROUP_ID, SUDOERS, BOT_ID

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
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["create_fed_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_name"])
    fed_name = message.text.split(None, 1)[1]
    fed_id = await generate_fed_id(user.id)
    await create_federation(fed_id, fed_name, user.id, user.mention, LOG_GROUP_ID)
    await message.reply_text(MESSAGES["new_fed_created"].format(fed_name=fed_name, fed_id=fed_id))
    try:
        await app.send_message(LOG_GROUP_ID, f"New Federation: <b>{fed_name}</b>\nID: <pre>{fed_id}</pre>", parse_mode="html")
    except Exception:
        pass

@app.on_message(filters.command("delfed"))
async def del_fed(client: Client, message: Message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["delete_fed_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != user.id and user.id not in SUDOERS:
        return await message.reply_text(MESSAGES["only_fed_owners_can_delete"])
    await delete_federation(fed_id)
    await message.reply_text(MESSAGES["fed_deleted"].format(fed_name=fed_info['fed_name']))

@app.on_message(filters.command("fedtransfer"))
async def fed_transfer(client: Client, message: Message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["transfer_fed_private"])
    if len(message.command) < 3:
        return await message.reply_text(MESSAGES["transfer_fed_usage"])
    user_id, fed_id = await extract_user_and_reason(message)
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != user.id:
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
    user = message.from_user
    msg = message
    args = msg.text.split(None, 2)
    if len(args) < 3:
        return await msg.reply_text("usage: /renamefed fed_id newname")
    fed_id, newname = args[1], args[2]
    verify_fed = await get_fed_info(fed_id)
    if not verify_fed:
        return await msg.reply_text("This fed does not exist in my database!")
    if await is_user_fed_owner(fed_id, user.id):
        await fedsdb.update_one(
            {"fed_id": str(fed_id)},
            {"$set": {"fed_name": str(newname), "owner_id": int(user.id)}},
            upsert=True,
        )
        await msg.reply_text(f"Successfully renamed your fed name to {newname}!")
    else:
        await msg.reply_text("Only federation owner can do this!")

@app.on_message(filters.command(["setfedlog", "unsetfedlog"]))
async def set_unset_fed_log(client: Client, message: Message):
    user = message.from_user
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
    if fed_info["owner_id"] != user.id:
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
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["join_fed_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id_join"])
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if not await is_group_admin(message.chat.id, user.id):
        return await message.reply_text(MESSAGES["only_group_admins_can_join"])
    await chat_join_fed(fed_id, message.chat.title, message.chat.id)
    await message.reply_text(MESSAGES["group_joined_federation"].format(fed_name=fed_info['fed_name']))

@app.on_message(filters.command("leavefed"))
async def leave_fed(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["leave_fed_private"])
    fed_id = await get_fed_id(chat.id)
    fed_info = await get_fed_info(fed_id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    if not await is_group_admin(chat.id, user.id):
        return await message.reply_text(MESSAGES["only_group_admins_can_leave"])
    await chat_leave_fed(chat.id)
    await message.reply_text(MESSAGES["group_left_federation"].format(fed_name=fed_info['fed_name']))

@app.on_message(filters.command("fedchats"))
async def fed_chats(client: Client, message: Message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fedchats_private"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id_fedchats"])
    fed_id = message.command[1]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text(MESSAGES["fed_does_not_exist"])
    if user.id not in fed_info["fadmins"] + [fed_info["owner_id"]]:
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
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fpromote_private"])
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    if not await is_user_fed_owner(fed_id, user.id):
        return await message.reply_text(MESSAGES["only_fed_owners_can_promote"])
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    await add_fed_admin(fed_id, user_id)
    await message.reply_text(MESSAGES["user_promoted"])

@app.on_message(filters.command("fdemote"))
async def fdemote(client: Client, message: Message):
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fdemote_private"])
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    if not await is_user_fed_owner(fed_id, user.id):
        return await message.reply_text(MESSAGES["only_fed_owners_can_demote"])
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    await remove_fed_admin(fed_id, user_id)
    await message.reply_text(MESSAGES["user_demoted"])

@app.on_message(filters.command(["fban", "sfban"]))
async def fban_user(client: Client, message: Message):
    chat = message.chat
    from_user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fban_private"])
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = await get_fed_info(fed_id)
    fed_owner = fed_info["owner_id"]
    fed_admins = fed_info["fadmins"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id in all_admins or from_user.id in SUDOERS:
        pass
    else:
        return await message.reply_text(MESSAGES["only_fed_admins_can_ban"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    user_id, reason = await extract_user_and_reason(message)
    try:
        user = await app.get_users(user_id)
    except PeerIdInvalid:
        return await message.reply_text("Sorry, I've never met this user.")
    if user_id in all_admins or user_id in SUDOERS:
        return await message.reply_text("I can't ban that user.")
    check_user = await check_banned_user(fed_id, user_id)
    if check_user:
        reason = check_user["reason"]
        date = check_user["date"]
        return await message.reply_text(f"**User {user.mention} was already Fed Banned.\n\nReason: {reason}.\nDate: {date}.**")
    if not reason:
        return await message.reply_text("No reason provided.")
    served_chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(f"**Fed Banning {user.mention}!**\n**This Action Should Take About {len(served_chats)} Seconds.**")
    await add_banned_user(fed_id, user_id, reason)
    number_of_chats = 0
    for served_chat in served_chats:
        try:
            chat_member = await app.get_chat_member(served_chat, user.id)
            if chat_member.status == ChatMemberStatus.MEMBER:
                await app.ban_chat_member(served_chat, user.id)
                if served_chat != chat.id:
                    if not message.text.startswith("/s"):
                        await app.send_message(served_chat, f"**Fed Banned {user.mention}!**")
                number_of_chats += 1
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    try:
        await app.send_message(user.id, f"Hello, You have been fed banned by {from_user.mention}, you can appeal for this ban by talking to them.")
    except Exception:
        pass
    await m.edit(f"Fed Banned {user.mention}!")
    ban_text = f"""
__**New Federation Ban**__
**Origin:** {message.chat.title} [`{message.chat.id}`]
**Admin:** {from_user.mention}
**Banned User:** {user.mention}
**Banned User ID:** `{user_id}`
**Reason:** __{reason}__
**Chats:** `{number_of_chats}`"""
    try:
        m2 = await app.send_message(fed_info["log_group_id"], text=ban_text, disable_web_page_preview=True)
        await m.edit(f"Fed Banned {user.mention}!\nAction Log: {m2.link}", disable_web_page_preview=True)
    except Exception:
        await message.reply_text("User Fedbanned, But This Fedban Action Wasn't Logged. Add Me In LOG_GROUP.")

@app.on_message(filters.command(["unfban", "sunfban"]))
async def funban_user(client: Client, message: Message):
    chat = message.chat
    from_user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["unfban_private"])
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = await get_fed_info(fed_id)
    fed_owner = fed_info["owner_id"]
    fed_admins = fed_info["fadmins"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id in all_admins or from_user.id in SUDOERS:
        pass
    else:
        return await message.reply_text(MESSAGES["only_fed_admins_can_unban"])
    if len(message.command) < 2:
        return await message.reply_text(MESSAGES["provide_fed_id"])
    user_id, reason = await extract_user_and_reason(message)
    user = await app.get_users(user_id)
    if not reason:
        return await message.reply_text("No reason provided.")
    served_chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(f"**Fed UnBanning {user.mention}!**\n**This Action Should Take About {len(served_chats)} Seconds.**")
    await remove_banned_user(fed_id, user_id)
    number_of_chats = 0
    for served_chat in served_chats:
        try:
            chat_member = await app.get_chat_member(served_chat, user.id)
            if chat_member.status == ChatMemberStatus.BANNED:
                await app.unban_chat_member(served_chat, user.id)
                if served_chat != chat.id:
                    if not message.text.startswith("/s"):
                        await app.send_message(served_chat, f"**Fed UnBanned {user.mention}!**")
                number_of_chats += 1
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    try:
        await app.send_message(user.id, f"Hello, You have been fed unbanned by {from_user.mention}, you can thank them for their action.")
    except Exception:
        pass
    await m.edit(f"Fed UnBanned {user.mention}!")
    unban_text = f"""
__**New Federation UnBan**__
**Origin:** {message.chat.title} [`{message.chat.id}`]
**Admin:** {from_user.mention}
**UnBanned User:** {user.mention}
**UnBanned User ID:** `{user_id}`
**Reason:** __{reason}__
**Chats:** `{number_of_chats}`"""
    try:
        m2 = await app.send_message(fed_info["log_group_id"], text=unban_text, disable_web_page_preview=True)
        await m.edit(f"Fed UnBanned {user.mention}!\nAction Log: {m2.link}", disable_web_page_preview=True)
    except Exception:
        await message.reply_text("User Fedunbanned, But This Fedunban Action Wasn't Logged. Add Me In LOG_GROUP.")

@app.on_message(filters.command("fedstat"))
async def fedstat(client: Client, message: Message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fedstat_private"])
    if len(message.command) < 2:
        user_id = user.id
    else:
        user_id, fed_id = await extract_user_and_reason(message)
        if not user_id:
            user_id = message.from_user.id
            fed_id = message.text.split(" ", 1)[1].strip()
        if not fed_id:
            return await status(message, user_id)
    info = await get_fed_info(fed_id)
    if not info:
        await message.reply_text("Please enter a valid fed id")
    else:
        check_user = await check_banned_user(fed_id, user_id)
        if check_user:
            user = await app.get_users(user_id)
            reason = check_user["reason"]
            date = check_user["date"]
            return await message.reply_text(f"**User {user.mention} was Fed Banned for:\n\nReason: {reason}.\nDate: {date}.**")
        else:
            await message.reply_text(f"**User {user.mention} is not Fed Banned in this federation.**")

@app.on_message(filters.command("fbroadcast"))
async def fbroadcast_message(client: Client, message: Message):
    chat = message.chat
    from_user = message.from_user
    reply_message = message.reply_to_message
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(MESSAGES["fbroadcast_private"])
    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = await get_fed_info(fed_id)
    fed_owner = fed_info["owner_id"]
    fed_admins = fed_info["fadmins"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id in all_admins or from_user.id in SUDOERS:
        pass
    else:
        return await message.reply_text(MESSAGES["only_fed_admins_can_broadcast"])
    if not reply_message:
        return await message.reply_text(MESSAGES["reply_to_broadcast"])
    sleep_time = 0.1
    sent = 0
    chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(f"Broadcast in progress, will take {len(chats) * sleep_time} seconds.")
    to_copy = not reply_message.poll
    for i in chats:
        try:
            if to_copy:
                await reply_message.copy(i)
            else:
                await reply_message.forward(i)
            sent += 1
            await asyncio.sleep(sleep_time)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    await m.edit(f"**Broadcasted Message In {sent} Chats.**")

@app.on_callback_query(filters.regex("rmfed_(.*)"))
async def del_fed_button(client, cb):
    query = cb.data
    fed_id = query.split("_")[1]
    if fed_id == "cancel":
        await cb.message.edit_text("Federation deletion cancelled")
        return
    getfed = await get_fed_info(fed_id)
    if getfed:
        delete = fedsdb.delete_one({"fed_id": str(fed_id)})
        if delete:
            await cb.message.edit_text(
                "You have removed your Federation! Now all the Groups that are connected with `{}` do not have a Federation.".format(
                    getfed["fed_name"]
                ),
                parse_mode="markdown",
            )

@app.on_callback_query(filters.regex("trfed_(.*)"))
async def fedtransfer_button(client, cb):
    query = cb.data
    data = query.split("_")[1]
    if data == "cancel":
        return await cb.message.edit_text("Federation transfer cancelled")
    data2 = data.split("|", 1)
    new_owner_id = int(data2[0])
    fed_id = data2[1]
    transferred = await transfer_owner(fed_id, new_owner_id)
    if transferred:
        await cb.message.edit_text("**Successfully transferred ownership to new owner.**")

@app.on_callback_query(filters.regex("fed_(.*)"))
async def fed_owner_help(client, cb):
    query = cb.data
    data = query.split("_")[1]
    if data == "owner":
        text = MESSAGES["fed_owner_commands"]
    elif data == "admin":
        text = MESSAGES["fed_admin_commands"]
    else:
        text = MESSAGES["user_commands"]
    await cb.message.edit(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="help_module(federation)")]]),
        parse_mode="markdown",
    )

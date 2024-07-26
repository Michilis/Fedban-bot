from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from bot.utils import generate_fed_id, create_confirmation_markup, extract_user_and_reason
from bot.db import (
    create_federation, delete_federation, get_fed_info, get_feds_by_owner,
    add_fed_admin, remove_fed_admin, add_banned_user, remove_banned_user, set_log_chat,
    get_fed_id, is_user_fed_owner, check_banned_user, chat_join_fed, chat_leave_fed,
    search_fed_by_id, is_group_admin, chat_id_and_names_in_fed,
    transfer_owner, get_user_fstatus
)
from bot.messages import MESSAGES
from config import LOG_GROUP_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(MESSAGES["start_message"])

async def fedhelp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin")],
            [InlineKeyboardButton("Federation Owner Commands", callback_data="fed_owner")],
            [InlineKeyboardButton("User Commands", callback_data="user")],
        ]
    )
    await update.message.reply_text(MESSAGES["help_menu"], reply_markup=keyboard)

async def new_fed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["create_fed_private"])
        return
    if len(context.args) < 1:
        await update.message.reply_text(MESSAGES["provide_fed_name"])
        return
    fed_name = " ".join(context.args)
    fed_id = await generate_fed_id(update.message.from_user.id)
    await create_federation(fed_id, fed_name, update.message.from_user.id, update.message.from_user.mention_html(), LOG_GROUP_ID)
    await update.message.reply_text(MESSAGES["new_fed_created"].format(fed_name=fed_name, fed_id=fed_id))

async def del_fed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["delete_fed_private"])
        return
    if len(context.args) < 1:
        await update.message.reply_text(MESSAGES["provide_fed_id"])
        return
    fed_id = context.args[0]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    if fed_info["owner_id"] != update.message.from_user.id:
        await update.message.reply_text(MESSAGES["only_fed_owners_can_delete"])
        return
    await delete_federation(fed_id)
    await update.message.reply_text(MESSAGES["fed_deleted"].format(fed_name=fed_info['fed_name']))

async def fed_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["transfer_fed_private"])
        return
    if len(context.args) < 2:
        await update.message.reply_text(MESSAGES["transfer_fed_usage"])
        return
    user_id, fed_id = extract_user_and_reason(update.message)
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    if fed_info["owner_id"] != update.message.from_user.id:
        await update.message.reply_text(MESSAGES["only_fed_owners_can_transfer"])
        return
    await add_fed_admin(fed_id, user_id)
    await update.message.reply_text(MESSAGES["fed_transferred"].format(fed_name=fed_info['fed_name'], user_id=user_id))

async def my_feds(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    feds = await get_feds_by_owner(update.message.from_user.id)
    if not feds:
        await update.message.reply_text(MESSAGES["no_federations_created"])
        return
    fed_list = "\n".join([f"Name: {fed['fed_name']} - ID: {fed['fed_id']}" for fed in feds])
    await update.message.reply_text(MESSAGES["your_federations"].format(fed_list=fed_list))

async def rename_fed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(MESSAGES["rename_fed_usage"])
        return
    fed_id, new_name = context.args[0], " ".join(context.args[1:])
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    if fed_info["owner_id"] != update.message.from_user.id:
        await update.message.reply_text(MESSAGES["only_fed_owners_can_rename"])
        return
    conn = await get_conn()
    await conn.execute('UPDATE federations SET fed_name = $1 WHERE fed_id = $2', new_name, fed_id)
    await conn.close()
    await update.message.reply_text(MESSAGES["fed_renamed"].format(new_name=new_name))

async def set_unset_fed_log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        if len(context.args) < 2:
            await update.message.reply_text(MESSAGES["set_unset_fed_log_private"].format(command=update.message.text))
            return
        chat_id = context.args[0]
        fed_id = context.args[1]
    else:
        if len(context.args) < 1:
            await update.message.reply_text(MESSAGES["provide_fed_id"])
            return
        chat_id = update.message.chat.id
        fed_id = context.args[0]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    if fed_info["owner_id"] != update.message.from_user.id:
        await update.message.reply_text(MESSAGES["only_fed_owners_can_set_unset_log"])
        return
    log_group_id = LOG_GROUP_ID if "unset" in update.message.text else chat_id
    await set_log_chat(fed_id, log_group_id)
    await update.message.reply_text(MESSAGES["log_channel_set"] if "set" in update.message.text else MESSAGES["log_channel_unset"])

async def chat_fed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["chat_fed_private"])
        return
    fed_id = await get_fed_id(update.message.chat.id)
    if not fed_id:
        await update.message.reply_text(MESSAGES["group_not_in_federation"])
        return
    fed_info = await get_fed_info(fed_id)
    await update.message.reply_text(MESSAGES["group_in_federation"].format(fed_name=fed_info['fed_name'], fed_id=fed_id))

async def join_fed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["join_fed_private"])
        return
    if len(context.args) < 1:
        await update.message.reply_text(MESSAGES["provide_fed_id_join"])
        return
    fed_id = context.args[0]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    if not await is_group_admin(update.message.chat.id, update.message.from_user.id):
        await update.message.reply_text(MESSAGES["only_group_admins_can_join"])
        return
    await chat_join_fed(fed_id, update.message.chat.title, update.message.chat.id)
    await update.message.reply_text(MESSAGES["group_joined_federation"].format(fed_name=fed_info['fed_name']))

async def leave_fed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["leave_fed_private"])
        return
    fed_id = await get_fed_id(update.message.chat.id)
    if not fed_id:
        await update.message.reply_text(MESSAGES["group_not_in_federation"])
        return
    fed_info = await get_fed_info(fed_id)
    if not await is_group_admin(update.message.chat.id, update.message.from_user.id):
        await update.message.reply_text(MESSAGES["only_group_admins_can_leave"])
        return
    await chat_leave_fed(update.message.chat.id)
    await update.message.reply_text(MESSAGES["group_left_federation"].format(fed_name=fed_info['fed_name']))

async def fed_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["fedchats_private"])
        return
    if len(context.args) < 1:
        await update.message.reply_text(MESSAGES["provide_fed_id_fedchats"])
        return
    fed_id = context.args[0]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    if update.message.from_user.id not in fed_info["fadmins"] + [fed_info["owner_id"]]:
        await update.message.reply_text(MESSAGES["only_fed_admins_can_check_fedchats"])
        return
    chat_ids, chat_names = await chat_id_and_names_in_fed(fed_id)
    chat_list = "\n".join([f"{chat_name} (`{chat_id}`)" for chat_id, chat_name in zip(chat_ids, chat_names)])
    await update.message.reply_text(MESSAGES["fed_chats_list"].format(fed_name=fed_info['fed_name'], chat_list=chat_list))

async def fed_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        fed_id = await get_fed_id(update.message.chat.id)
        if not fed_id:
            await update.message.reply_text(MESSAGES["provide_fed_id"])
            return
    else:
        fed_id = context.args[0]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    await update.message.reply_text(
        MESSAGES["fed_info_list"].format(
            fed_name=fed_info['fed_name'],
            owner_mention=fed_info['owner_mention'],
            admins=len(fed_info['fadmins']),
            banned_users=len(fed_info['banned_users']),
            chats=len(fed_info['chat_ids'])
        )
    )

async def fed_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        fed_id = await get_fed_id(update.message.chat.id)
        if not fed_id:
            await update.message.reply_text(MESSAGES["provide_fed_id"])
            return
    else:
        fed_id = context.args[0]
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        await update.message.reply_text(MESSAGES["fed_does_not_exist"])
        return
    admin_ids = fed_info["fadmins"]
    admins = [await context.bot.get_chat(admin_id) for admin_id in admin_ids]
    admins_list = "\n".join([f"{admin.mention_html()} ({admin.id})" for admin in admins])
    await update.message.reply_text(MESSAGES["fed_admins_list"].format(owner_mention=fed_info['owner_mention'], admins_list=admins_list))

async def fpromote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["fpromote_private"])
        return
    fed_id = await get_fed_id(update.message.chat.id)
    if not fed_id:
        await update.message.reply_text(MESSAGES["group_not_in_federation"])
        return
    if not await is_user_fed_owner(fed_id, update.message.from_user.id):
        await update.message.reply_text(MESSAGES["only_fed_owners_can_promote"])
        return
    user_id, _ = extract_user_and_reason(update.message)
    if not user_id:
        await update.message.reply_text(MESSAGES["provide_fed_id"])
        return
    await add_fed_admin(fed_id, user_id)
    await update.message.reply_text(MESSAGES["user_promoted"])

async def fdemote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["fdemote_private"])
        return
    fed_id = await get_fed_id(update.message.chat.id)
    if not fed_id:
        await update.message.reply_text(MESSAGES["group_not_in_federation"])
        return
    if not await is_user_fed_owner(fed_id, update.message.from_user.id):
        await update.message.reply_text(MESSAGES["only_fed_owners_can_demote"])
        return
    user_id, _ = extract_user_and_reason(update.message)
    if not user_id:
        await update.message.reply_text(MESSAGES["provide_fed_id"])
        return
    await remove_fed_admin(fed_id, user_id)
    await update.message.reply_text(MESSAGES["user_demoted"])

async def fban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["fban_private"])
        return
    fed_id = await get_fed_id(update.message.chat.id)
    if not fed_id:
        await update.message.reply_text(MESSAGES["group_not_in_federation"])
        return
    if not await is_user_fed_owner(fed_id, update.message.from_user.id):
        await update.message.reply_text(MESSAGES["only_fed_admins_can_ban"])
        return
    user_id, reason = extract_user_and_reason(update.message)
    if not user_id:
        await update.message.reply_text(MESSAGES["provide_fed_id"])
        return
    await add_banned_user(fed_id, user_id, reason)
    await update.message.reply_text(MESSAGES["user_banned"])

async def funban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["unfban_private"])
        return
    fed_id = await get_fed_id(update.message.chat.id)
    if not fed_id:
        await update.message.reply_text(MESSAGES["group_not_in_federation"])
        return
    if not await is_user_fed_owner(fed_id, update.message.from_user.id):
        await update.message.reply_text(MESSAGES["only_fed_admins_can_unban"])
        return
    user_id, reason = extract_user_and_reason(update.message)
    if not user_id:
        await update.message.reply_text(MESSAGES["provide_fed_id"])
        return
    await remove_banned_user(fed_id, user_id)
    await update.message.reply_text(MESSAGES["user_unbanned"])

async def fed_stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["fedstat_private"])
        return
    if len(context.args) < 1:
        user_id = update.message.from_user.id
    else:
        user_id = int(context.args[0])
    status = await get_user_fstatus(user_id)
    user = await context.bot.get_chat(user_id)
    if status:
        status_list = "\n\n".join(
            [f"{i + 1}) **Fed Name:** {fed['fed_name']}\n  **Fed Id:** `{fed['fed_id']}`" for i, fed in enumerate(status)]
        )
        await update.message.reply_text(MESSAGES["user_fed_status"].format(user=user.mention_html(), status_list=status_list))
    else:
        await update.message.reply_text(MESSAGES["user_not_banned"].format(user=user.mention_html()))

async def fbroadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == ChatType.PRIVATE:
        await update.message.reply_text(MESSAGES["fbroadcast_private"])
        return
    if not update.message.reply_to_message:
        await update.message.reply_text(MESSAGES["reply_to_broadcast"])
        return
    fed_id = await get_fed_id(update.message.chat.id)
    if not fed_id:
        await update.message.reply_text(MESSAGES["group_not_in_federation"])
        return
    fed_info = await get_fed_info(fed_id)
    if not await is_user_fed_owner(fed_id, update.message.from_user.id):
        await update.message.reply_text(MESSAGES["only_fed_admins_can_broadcast"])
        return
    chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await update.message.reply_text(MESSAGES["broadcast_in_progress"].format(seconds=len(chats)))
    for chat_id in chats:
        try:
            await update.message.reply_to_message.copy(chat_id)
            await asyncio.sleep(0.1)
        except Exception:
            pass
    await m.edit_text(MESSAGES["broadcast_done"].format(count=len(chats)))

def register_command_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fedhelp", fedhelp))
    app.add_handler(CommandHandler("newfed", new_fed))
    app.add_handler(CommandHandler("delfed", del_fed))
    app.add_handler(CommandHandler("fedtransfer", fed_transfer))
    app.add_handler(CommandHandler("myfeds", my_feds))
    app.add_handler(CommandHandler("renamefed", rename_fed))
    app.add_handler(CommandHandler(["setfedlog", "unsetfedlog"], set_unset_fed_log))
    app.add_handler(CommandHandler("chatfed", chat_fed))
    app.add_handler(CommandHandler("joinfed", join_fed))
    app.add_handler(CommandHandler("leavefed", leave_fed))
    app.add_handler(CommandHandler("fedchats", fed_chats))
    app.add_handler(CommandHandler("fedinfo", fed_info))
    app.add_handler(CommandHandler("fedadmins", fed_admins))
    app.add_handler(CommandHandler("fpromote", fpromote))
    app.add_handler(CommandHandler("fdemote", fdemote))
    app.add_handler(CommandHandler(["fban", "sfban"], fban_user))
    app.add_handler(CommandHandler(["unfban", "sunfban"], funban_user))
    app.add_handler(CommandHandler("fedstat", fed_stat))
    app.add_handler(CommandHandler("fbroadcast", fbroadcast_message))

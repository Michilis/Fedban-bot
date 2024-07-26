from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from bot.app import bot  # Import the bot instance
from bot.db import (
    create_federation, delete_federation, get_fed_info, get_feds_by_owner,
    add_fed_admin, remove_fed_admin, add_banned_user, remove_banned_user, set_log_chat,
    get_fed_id, is_user_fed_owner, check_banned_user, chat_join_fed, chat_leave_fed,
    search_fed_by_id, is_group_admin, chat_id_and_names_in_fed,
    transfer_owner, get_user_fstatus
)
from bot.utils import generate_fed_id, create_confirmation_markup, extract_user_and_reason
from bot.messages import MESSAGES
from config import LOG_GROUP_ID

def start(update: Update, context: CallbackContext):
    update.message.reply_text(MESSAGES["start_message"])

def fedhelp(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin")],
            [InlineKeyboardButton("Federation Owner Commands", callback_data="fed_owner")],
            [InlineKeyboardButton("User Commands", callback_data="user")],
        ]
    )
    update.message.reply_text(MESSAGES["help_menu"], reply_markup=keyboard)

def new_fed(update: Update, context: CallbackContext):
    if update.message.chat.type != "private":
        return update.message.reply_text(MESSAGES["create_fed_private"])
    if len(context.args) < 1:
        return update.message.reply_text(MESSAGES["provide_fed_name"])
    fed_name = " ".join(context.args)
    fed_id = generate_fed_id(update.message.from_user.id)
    create_federation(fed_id, fed_name, update.message.from_user.id, update.message.from_user.mention_html(), LOG_GROUP_ID)
    update.message.reply_text(MESSAGES["new_fed_created"].format(fed_name=fed_name, fed_id=fed_id))

def del_fed(update: Update, context: CallbackContext):
    if update.message.chat.type != "private":
        return update.message.reply_text(MESSAGES["delete_fed_private"])
    if len(context.args) < 1:
        return update.message.reply_text(MESSAGES["provide_fed_id"])
    fed_id = context.args[0]
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != update.message.from_user.id:
        return update.message.reply_text(MESSAGES["only_fed_owners_can_delete"])
    delete_federation(fed_id)
    update.message.reply_text(MESSAGES["fed_deleted"].format(fed_name=fed_info['fed_name']))

def fed_transfer(update: Update, context: CallbackContext):
    if update.message.chat.type != "private":
        return update.message.reply_text(MESSAGES["transfer_fed_private"])
    if len(context.args) < 2:
        return update.message.reply_text(MESSAGES["transfer_fed_usage"])
    user_id, fed_id = extract_user_and_reason(update.message)
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != update.message.from_user.id:
        return update.message.reply_text(MESSAGES["only_fed_owners_can_transfer"])
    add_fed_admin(fed_id, user_id)
    update.message.reply_text(MESSAGES["fed_transferred"].format(fed_name=fed_info['fed_name'], user_id=user_id))

def my_feds(update: Update, context: CallbackContext):
    feds = get_feds_by_owner(update.message.from_user.id)
    if not feds:
        return update.message.reply_text(MESSAGES["no_federations_created"])
    fed_list = "\n".join([f"Name: {fed['fed_name']} - ID: {fed['fed_id']}" for fed in feds])
    update.message.reply_text(MESSAGES["your_federations"].format(fed_list=fed_list))

def rename_fed(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        return update.message.reply_text(MESSAGES["rename_fed_usage"])
    fed_id, new_name = context.args[0], " ".join(context.args[1:])
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != update.message.from_user.id:
        return update.message.reply_text(MESSAGES["only_fed_owners_can_rename"])
    conn = get_conn()
    conn.execute('UPDATE federations SET fed_name = $1 WHERE fed_id = $2', new_name, fed_id)
    conn.close()
    update.message.reply_text(MESSAGES["fed_renamed"].format(new_name=new_name))

def set_unset_fed_log(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        if len(context.args) < 2:
            return update.message.reply_text(MESSAGES["set_unset_fed_log_private"].format(command=context.args[0]))
        chat_id = context.args[0]
        fed_id = context.args[1]
    else:
        if len(context.args) < 1:
            return update.message.reply_text(MESSAGES["provide_fed_id"])
        chat_id = update.message.chat.id
        fed_id = context.args[0]
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    if fed_info["owner_id"] != update.message.from_user.id:
        return update.message.reply_text(MESSAGES["only_fed_owners_can_set_unset_log"])
    log_group_id = LOG_GROUP_ID if "unset" in context.args[0] else chat_id
    set_log_chat(fed_id, log_group_id)
    update.message.reply_text(MESSAGES["log_channel_set"] if "set" in context.args[0] else MESSAGES["log_channel_unset"])

def chat_fed(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["chat_fed_private"])
    fed_id = get_fed_id(update.message.chat.id)
    if not fed_id:
        return update.message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = get_fed_info(fed_id)
    update.message.reply_text(MESSAGES["group_in_federation"].format(fed_name=fed_info['fed_name'], fed_id=fed_id))

def join_fed(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["join_fed_private"])
    if len(context.args) < 1:
        return update.message.reply_text(MESSAGES["provide_fed_id_join"])
    fed_id = context.args[0]
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    if not is_group_admin(update.message.chat.id, update.message.from_user.id):
        return update.message.reply_text(MESSAGES["only_group_admins_can_join"])
    chat_join_fed(fed_id, update.message.chat.title, update.message.chat.id)
    update.message.reply_text(MESSAGES["group_joined_federation"].format(fed_name=fed_info['fed_name']))

def leave_fed(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["leave_fed_private"])
    fed_id = get_fed_id(update.message.chat.id)
    if not fed_id:
        return update.message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = get_fed_info(fed_id)
    if not is_group_admin(update.message.chat.id, update.message.from_user.id):
        return update.message.reply_text(MESSAGES["only_group_admins_can_leave"])
    chat_leave_fed(update.message.chat.id)
    update.message.reply_text(MESSAGES["group_left_federation"].format(fed_name=fed_info['fed_name']))

def fed_chats(update: Update, context: CallbackContext):
    if update.message.chat.type != "private":
        return update.message.reply_text(MESSAGES["fedchats_private"])
    if len(context.args) < 1:
        return update.message.reply_text(MESSAGES["provide_fed_id_fedchats"])
    fed_id = context.args[0]
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    if update.message.from_user.id not in fed_info["fadmins"] + [fed_info["owner_id"]]:
        return update.message.reply_text(MESSAGES["only_fed_admins_can_check_fedchats"])
    chat_ids, chat_names = chat_id_and_names_in_fed(fed_id)
    chat_list = "\n".join([f"{chat_name} (`{chat_id}`)" for chat_id, chat_name in zip(chat_ids, chat_names)])
    update.message.reply_text(MESSAGES["fed_chats_list"].format(fed_name=fed_info['fed_name'], chat_list=chat_list))

def fed_info(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        fed_id = get_fed_id(update.message.chat.id)
        if not fed_id:
            return update.message.reply_text(MESSAGES["provide_fed_id"])
    else:
        fed_id = context.args[0]
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    update.message.reply_text(
        MESSAGES["fed_info_list"].format(
            fed_name=fed_info['fed_name'],
            owner_mention=fed_info['owner_mention'],
            admins=len(fed_info['fadmins']),
            banned_users=len(fed_info['banned_users']),
            chats=len(fed_info['chat_ids'])
        )
    )

def fed_admins(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        fed_id = get_fed_id(update.message.chat.id)
        if not fed_id:
            return update.message.reply_text(MESSAGES["provide_fed_id"])
    else:
        fed_id = context.args[0]
    fed_info = get_fed_info(fed_id)
    if not fed_info:
        return update.message.reply_text(MESSAGES["fed_does_not_exist"])
    admin_ids = fed_info["fadmins"]
    admins = [bot.get_chat_member(update.message.chat.id, admin_id) for admin_id in admin_ids]
    admins_list = "\n".join([f"{admin.user.mention_html()} ({admin.user.id})" for admin in admins])
    update.message.reply_text(MESSAGES["fed_admins_list"].format(owner_mention=fed_info['owner_mention'], admins_list=admins_list))

def fpromote(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["fpromote_private"])
    fed_id = get_fed_id(update.message.chat.id)
    if not fed_id:
        return update.message.reply_text(MESSAGES["group_not_in_federation"])
    if not is_user_fed_owner(fed_id, update.message.from_user.id):
        return update.message.reply_text(MESSAGES["only_fed_owners_can_promote"])
    user_id, _ = extract_user_and_reason(update.message)
    if not user_id:
        return update.message.reply_text(MESSAGES["provide_fed_id"])
    add_fed_admin(fed_id, user_id)
    update.message.reply_text(MESSAGES["user_promoted"])

def fdemote(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["fdemote_private"])
    fed_id = get_fed_id(update.message.chat.id)
    if not fed_id:
        return update.message.reply_text(MESSAGES["group_not_in_federation"])
    if not is_user_fed_owner(fed_id, update.message.from_user.id):
        return update.message.reply_text(MESSAGES["only_fed_owners_can_demote"])
    user_id, _ = extract_user_and_reason(update.message)
    if not user_id:
        return update.message.reply_text(MESSAGES["provide_fed_id"])
    remove_fed_admin(fed_id, user_id)
    update.message.reply_text(MESSAGES["user_demoted"])

def fban_user(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["fban_private"])
    fed_id = get_fed_id(update.message.chat.id)
    if not fed_id:
        return update.message.reply_text(MESSAGES["group_not_in_federation"])
    if not is_user_fed_owner(fed_id, update.message.from_user.id):
        return update.message.reply_text(MESSAGES["only_fed_admins_can_ban"])
    user_id, reason = extract_user_and_reason(update.message)
    if not user_id:
        return update.message.reply_text(MESSAGES["provide_fed_id"])
    add_banned_user(fed_id, user_id, reason)
    update.message.reply_text(MESSAGES["user_banned"])

def funban_user(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["unfban_private"])
    fed_id = get_fed_id(update.message.chat.id)
    if not fed_id:
        return update.message.reply_text(MESSAGES["group_not_in_federation"])
    if not is_user_fed_owner(fed_id, update.message.from_user.id):
        return update.message.reply_text(MESSAGES["only_fed_admins_can_unban"])
    user_id, reason = extract_user_and_reason(update.message)
    if not user_id:
        return update.message.reply_text(MESSAGES["provide_fed_id"])
    remove_banned_user(fed_id, user_id)
    update.message.reply_text(MESSAGES["user_unbanned"])

def fed_stat(update: Update, context: CallbackContext):
    if update.message.chat.type != "private":
        return update.message.reply_text(MESSAGES["fedstat_private"])
    if len(context.args) < 1:
        user_id = update.message.from_user.id
    else:
        user_id = int(context.args[0])
    status = get_user_fstatus(user_id)
    user = bot.get_chat_member(update.message.chat.id, user_id).user
    if status:
        status_list = "\n\n".join(
            [f"{i + 1}) **Fed Name:** {fed['fed_name']}\n  **Fed Id:** `{fed['fed_id']}`" for i, fed in enumerate(status)]
        )
        update.message.reply_text(MESSAGES["user_fed_status"].format(user=user.mention_html(), status_list=status_list))
    else:
        return update.message.reply_text(MESSAGES["user_not_banned"].format(user=user.mention_html()))

def fbroadcast_message(update: Update, context: CallbackContext):
    if update.message.chat.type == "private":
        return update.message.reply_text(MESSAGES["fbroadcast_private"])
    if not update.message.reply_to_message:
        return update.message.reply_text(MESSAGES["reply_to_broadcast"])
    fed_id = get_fed_id(update.message.chat.id)
    if not fed_id:
        return update.message.reply_text(MESSAGES["group_not_in_federation"])
    fed_info = get_fed_info(fed_id)
    if not is_user_fed_owner(fed_id, update.message.from_user.id):
        return update.message.reply_text(MESSAGES["only_fed_admins_can_broadcast"])
    chats, _ = chat_id_and_names_in_fed(fed_id)
    m = update.message.reply_text(MESSAGES["broadcast_in_progress"].format(seconds=len(chats)))
    for chat_id in chats:
        try:
            update.message.reply_to_message.copy(chat_id)
            asyncio.sleep(0.1)
        except Exception:
            pass
    m.edit_text(MESSAGES["broadcast_done"].format(count=len(chats)))

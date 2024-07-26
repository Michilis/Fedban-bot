import logging
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from bot.db import (
    add_fed_admin,
    remove_fed_admin,
    add_banned_user,
    remove_banned_user,
    check_banned_user,
)
from config import DEBUGGING
from bot.messages import MESSAGES  # Updated import

if DEBUGGING:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

async def add_admin(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    user_id = int(context.args[1])
    await add_fed_admin(fed_id, user_id)
    await update.message.reply_text(MESSAGES["user_promoted"])

async def remove_admin(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    user_id = int(context.args[1])
    await remove_fed_admin(fed_id, user_id)
    await update.message.reply_text(MESSAGES["user_demoted"])

async def ban_user(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    user_id = int(context.args[1])
    reason = " ".join(context.args[2:]) if len(context.args) > 2 else "No reason provided"
    await add_banned_user(fed_id, user_id, reason)
    await update.message.reply_text(MESSAGES["user_banned"])

async def unban_user(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    user_id = int(context.args[1])
    await remove_banned_user(fed_id, user_id)
    await update.message.reply_text(MESSAGES["user_unbanned"])

async def check_ban(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    user_id = int(context.args[1])
    reason = await check_banned_user(fed_id, user_id)
    if reason:
        await update.message.reply_text(f"User is banned for reason: {reason}")
    else:
        await update.message.reply_text(MESSAGES["user_not_banned"].format(user=user_id))

def register_admin_command_handlers(app):
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("checkban", check_ban))

import logging
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from bot.db import (
    get_fed_id,
    chat_join_fed,
    chat_leave_fed,
    chat_id_and_names_in_fed,
)
from config import DEBUGGING, LOG_GROUP_ID
from messages import MESSAGES

if DEBUGGING:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

async def start(update: Update, context: CallbackContext) -> None:
    if DEBUGGING:
        logger.debug(f"User {update.message.from_user.id} issued /start command")
    await update.message.reply_text(MESSAGES["start_message"])

async def chat_join_fed(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    fed_id = context.args[0]
    await chat_join_fed(fed_id, chat_id)
    await update.message.reply_text(MESSAGES["group_joined_federation"].format(fed_name=fed_id))

async def chat_leave_fed(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    fed_id = await get_fed_id(chat_id)
    await chat_leave_fed(fed_id, chat_id)
    await update.message.reply_text(MESSAGES["group_left_federation"].format(fed_name=fed_id))

async def chat_id_and_names_in_fed(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    chats = await chat_id_and_names_in_fed(fed_id)
    if not chats:
        await update.message.reply_text(MESSAGES["no_chats_in_fed"])
    else:
        chat_list = "\n".join([f"{chat['chat_name']} (ID: {chat['chat_id']})" for chat in chats])
        await update.message.reply_text(f"Chats in federation:\n{chat_list}")

def register_user_command_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joinfed", chat_join_fed))
    app.add_handler(CommandHandler("leavefed", chat_leave_fed))
    app.add_handler(CommandHandler("fedchats", chat_id_and_names_in_fed))

import logging
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from bot.db import (
    create_federation,
    delete_federation,
    rename_federation,
    set_log_chat,
    unset_log_chat,
    get_feds_by_owner,
    transfer_owner,
)
from bot.utils import generate_fed_id
from config import DEBUGGING, LOG_GROUP_ID
from bot.messages import MESSAGES  # Updated import

if DEBUGGING:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

async def new_fed(update: Update, context: CallbackContext) -> None:
    fed_name = " ".join(context.args)
    fed_id = generate_fed_id(update.message.from_user.id)
    await create_federation(fed_id, fed_name, update.message.from_user.id, update.message.from_user.mention_html(), LOG_GROUP_ID)
    await update.message.reply_text(MESSAGES["new_fed_created"].format(fed_name=fed_name, fed_id=fed_id))

async def delete_fed(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    await delete_federation(fed_id)
    await update.message.reply_text(MESSAGES["fed_deleted"].format(fed_name=fed_id))

async def rename_fed(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    new_name = " ".join(context.args[1:])
    await rename_federation(fed_id, new_name)
    await update.message.reply_text(MESSAGES["fed_renamed"].format(new_name=new_name))

async def set_log(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    chat_id = int(context.args[1])
    await set_log_chat(fed_id, chat_id)
    await update.message.reply_text(MESSAGES["log_channel_set"])

async def unset_log(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    await unset_log_chat(fed_id)
    await update.message.reply_text(MESSAGES["log_channel_unset"])

def register_owner_command_handlers(app):
    app.add_handler(CommandHandler("newfed", new_fed))
    app.add_handler(CommandHandler("delfed", delete_fed))
    app.add_handler(CommandHandler("renamefed", rename_fed))
    app.add_handler(CommandHandler("setfedlog", set_log))
    app.add_handler(CommandHandler("unsetfedlog", unset_log))

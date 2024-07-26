import logging
from telegram import Update
from telegram.ext import CallbackContext
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
from config import DEBUGGING, LOG_GROUP_ID, MESSAGES

if DEBUGGING:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

async def new_fed(update: Update, context: CallbackContext) -> None:
    fed_name = " ".join(context.args)
    fed_id = generate_fed_id(update.message.from_user.id)
    await create_federation(fed_id, fed_name, update.message.from_user.id, update.message.from_user.mention_html(), LOG_GROUP_ID)
    await update.message.reply_text(MESSAGES["federation_created"])

async def delete_federation(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    await delete_federation(fed_id)
    await update.message.reply_text(MESSAGES["federation_deleted"])

async def rename_federation(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    new_name = " ".join(context.args[1:])
    await rename_federation(fed_id, new_name)
    await update.message.reply_text(MESSAGES["federation_renamed"])

async def set_log_chat(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    chat_id = int(context.args[1])
    await set_log_chat(fed_id, chat_id)
    await update.message.reply_text(MESSAGES["log_chat_set"])

async def unset_log_chat(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    await unset_log_chat(fed_id)
    await update.message.reply_text(MESSAGES["log_chat_unset"])

async def get_feds_by_owner(update: Update, context: CallbackContext) -> None:
    owner_id = update.message.from_user.id
    feds = await get_feds_by_owner(owner_id)
    if not feds:
        await update.message.reply_text(MESSAGES["no_federations_owned"])
    else:
        fed_list = "\n".join([f"{fed['fed_name']} (ID: {fed['fed_id']})" for fed in feds])
        await update.message.reply_text(f"Your federations:\n{fed_list}")

async def transfer_owner(update: Update, context: CallbackContext) -> None:
    fed_id = context.args[0]
    new_owner_id = int(context.args[1])
    await transfer_owner(fed_id, new_owner_id)
    await update.message.reply_text(MESSAGES["owner_transferred"])

def register_owner_command_handlers(app):
    app.add_handler(CommandHandler("newfed", new_fed))
    app.add_handler(CommandHandler("delfed", delete_federation))
    app.add_handler(CommandHandler("renamefed", rename_federation))
    app.add_handler(CommandHandler("setfedlog", set_log_chat))
    app.add_handler(CommandHandler("unsetfedlog", unset_log_chat))
    app.add_handler(CommandHandler("myfeds", get_feds_by_owner))
    app.add_handler(CommandHandler("fedtransfer", transfer_owner))

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from bot.messages import MESSAGES

def register_help_handlers(app):
    app.add_handler(CallbackQueryHandler(fed_admin_commands, pattern="fed_admin"))
    app.add_handler(CallbackQueryHandler(fed_owner_commands, pattern="fed_owner"))
    app.add_handler(CallbackQueryHandler(user_commands, pattern="user"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="back_to_main"))

async def fed_admin_commands(update, context):
    await update.callback_query.message.edit_text(
        MESSAGES["fed_admin_commands"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

async def fed_owner_commands(update, context):
    await update.callback_query.message.edit_text(
        MESSAGES["fed_owner_commands"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

async def user_commands(update, context):
    await update.callback_query.message.edit_text(
        MESSAGES["user_commands"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

async def back_to_main(update, context):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin")],
            [InlineKeyboardButton("Federation Owner Commands", callback_data="fed_owner")],
            [InlineKeyboardButton("User Commands", callback_data="user")],
        ]
    )
    await update.callback_query.message.edit_text(
        MESSAGES["help_menu"], reply_markup=keyboard
    )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.messages import MESSAGES

def fed_admin_commands(update: Update, context: CallbackContext):
    update.callback_query.message.edit_text(
        MESSAGES["fed_admin_commands"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

def fed_owner_commands(update: Update, context: CallbackContext):
    update.callback_query.message.edit_text(
        MESSAGES["fed_owner_commands"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

def user_commands(update: Update, context: CallbackContext):
    update.callback_query.message.edit_text(
        MESSAGES["user_commands"],
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

def back_to_main(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin")],
            [InlineKeyboardButton("Federation Owner Commands", callback_data="fed_owner")],
            [InlineKeyboardButton("User Commands", callback_data="user")],
        ]
    )
    update.callback_query.message.edit_text(
        MESSAGES["help_menu"], reply_markup=keyboard
    )

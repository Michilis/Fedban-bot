from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.messages import MESSAGES

def register_help_handlers(app):
    @app.on_callback_query(filters.regex(r"^fed_admin$"))
    async def fed_admin_commands(client, callback_query):
        await callback_query.message.edit_text(
            MESSAGES["fed_admin_commands"],
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
            )
        )

    @app.on_callback_query(filters.regex(r"^fed_owner$"))
    async def fed_owner_commands(client, callback_query):
        await callback_query.message.edit_text(
            MESSAGES["fed_owner_commands"],
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
            )
        )

    @app.on_callback_query(filters.regex(r"^user$"))
    async def user_commands(client, callback_query):
        await callback_query.message.edit_text(
            MESSAGES["user_commands"],
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
            )
        )

    @app.on_callback_query(filters.regex(r"^back_to_main$"))
    async def back_to_main(client, callback_query):
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin")],
                [InlineKeyboardButton("Federation Owner Commands", callback_data="fed_owner")],
                [InlineKeyboardButton("User Commands", callback_data="user")],
            ]
        )
        await callback_query.message.edit_text(
            MESSAGES["help_menu"], reply_markup=keyboard
        )

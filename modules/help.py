from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config

async def help_menu(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Fed Admin Commands", callback_data="fed_admin")],
            [InlineKeyboardButton("Federation Owner Commands", callback_data="fed_owner")],
            [InlineKeyboardButton("User Commands", callback_data="user")],
        ]
    )
    await message.reply(
        "Federations\n\n"
        "Ah, group management. It's all fun and games, until you start getting spammers in, and you need to ban them. "
        "Then you need to start banning more, and more, and it gets painful. "
        "But then you have multiple groups, and you don't want these spammers in any of your groups - how can you deal? "
        "Do you have to ban them manually, in all your groups?\n\n"
        "No more! With federations, you can make a ban in one chat overlap to all your other chats. "
        "You can even appoint federation admins, so that your trustworthiest admins can ban across all the chats that you want to protect.",
        reply_markup=keyboard
    )

# Callback handler for help menu buttons
@app.on_callback_query(filters.regex(r"^fed_admin$"))
async def fed_admin_commands(client, callback_query):
    await callback_query.message.edit_text(
        "Fed Admin Commands\n\n"
        "The following is the list of all fed admin commands. To run these, you have to be a federation admin in the current federation.\n\n"
        "Commands:\n"
        "- /fban: Bans a user from the current chat's federation\n"
        "- /unfban: Unbans a user from the current chat's federation\n"
        "- /feddemoteme <fedID>: Demote yourself from a fed.\n"
        "- /myfeds: List all feds you are an admin in.\n",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

@app.on_callback_query(filters.regex(r"^fed_owner$"))
async def fed_owner_commands(client, callback_query):
    await callback_query.message.edit_text(
        "Federation Owner Commands\n\n"
        "These are the list of available fed owner commands. To run these, you have to own the current federation.\n\n"
        "Owner Commands:\n"
        "- /newfed <fedname>: Creates a new federation with the given name. Only one federation per user.\n"
        "- /renamefed <fedname>: Rename your federation.\n"
        "- /delfed: Deletes your federation, and any information related to it. Will not unban any banned users.\n"
        "- /fedtransfer <reply/username/mention/userid>: Transfer your federation to another user.\n"
        "- /fedpromote: Promote a user to fedadmin in your fed. To avoid unwanted fedadmin, the user will get a message to confirm this.\n"
        "- /feddemote: Demote a federation admin in your fed.\n"
        "- /fednotif <yes/no/on/off>: Whether or not to receive PM notifications of every fed action.\n"
        "- /fedreason <yes/no/on/off>: Whether or not fedbans should require a reason.\n"
        "- /subfed <FedId>: Subscribe your federation to another. Users banned in the subscribed fed will also be banned in this one.\n"
        "  Note: This does not affect your banlist. You just inherit any bans.\n"
        "- /unsubfed <FedId>: Unsubscribes your federation from another. Bans from the other fed will no longer take effect.\n"
        "- /fedexport <csv/minicsv/json/human>: Get the list of currently banned users. Default output is CSV.\n"
        "- /fedimport <overwrite/keep> <csv/minicsv/json/human>: Import a list of banned users.\n"
        "- /setfedlog: Sets the current chat as the federation log. All federation events will be logged here.\n"
        "- /unsetfedlog: Unset the federation log. Events will no longer be logged.\n"
        "- /setfedlang: Change the language of the federation log. Note: This does not change the language of Rose's replies to fed commands, only the log channel.\n",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

@app.on_callback_query(filters.regex(r"^user$"))
async def user_commands(client, callback_query):
    await callback_query.message.edit_text(
        "User Commands\n\n"
        "These commands do not require you to be admin of a federation. These commands are for general commands, such as looking up information on a fed, or checking a user's fbans.\n\n"
        "Commands:\n"
        "- /fedinfo <FedID>: Information about a federation.\n"
        "- /fedadmins <FedID>: List the admins in a federation.\n"
        "- /fedsubs <FedID>: List all federations your federation is subscribed to.\n"
        "- /joinfed <FedID>: Join the current chat to a federation. A chat can only join one federation. Chat owners only.\n"
        "- /leavefed: Leave the current federation. Only chat owners can do this.\n"
        "- /fedstat: List all the federations that you have been banned in.\n"
        "- /fedstat <user ID>: List all the federations that a user has been banned in.\n"
        "- /fedstat <FedID>: Gives information about your ban in a federation.\n"
        "- /fedstat <user ID> <FedID>: Gives information about a user's ban in a federation.\n"
        "- /chatfed: Information about the federation the current chat is in.\n"
        "- /quietfed <yes/no/on/off>: Whether or not to send ban notifications when fedbanned users join the chat.\n",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Back", callback_data="back_to_main")]]
        )
    )

@app.on_callback_query(filters.regex(r"^back_to_main$"))
async def back_to_main(client, callback_query):
    await help_menu(client, callback_query.message)

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

async def help_menu(update: Update, context: CallbackContext) -> None:
    help_text = """
<b>Fedban Bot Commands:</b>

/start - Start the bot
/help - Show this help menu

<b>Federation Commands:</b>
/newfed <name> - Create a new federation
/joinfed <FedID> - Join a federation
/leavefed <FedID> - Leave a federation
/renamefed <new name> - Rename your federation
/fedinfo <FedID> - Get information about a federation

<b>Additional Commands:</b>
/ban <user> <reason> - Ban a user
/unban <user> - Unban a user
/banlist - List banned users
/whitelist <user> - Whitelist a user
/unwhitelist <user> - Remove a user from the whitelist
/whitelistlist - List whitelisted users
/warn <user> <reason> - Warn a user
/unwarn <user> - Remove a warning from a user
/warnlist - List warned users
/kick <user> - Kick a user
/promote <user> - Promote a user to admin
/demote <user> - Demote an admin
/mute <user> - Mute a user
/unmute <user> - Unmute a user

For detailed usage of each command, type /help <command>
"""
    await update.message.reply_text(help_text, parse_mode='HTML')

async def detailed_help(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Please specify a command to get help for.")
        return
    
    command = context.args[0].lower()
    detailed_help_texts = {
        "start": "/start - Start the bot and initialize it.",
        "help": "/help - Show the help menu with available commands.",
        "newfed": "/newfed <name> - Create a new federation with the given name.",
        "joinfed": "/joinfed <FedID> - Join a federation using the federation ID.",
        "leavefed": "/leavefed <FedID> - Leave a federation using the federation ID.",
        "renamefed": "/renamefed <new name> - Rename your federation to the new name.",
        "fedinfo": "/fedinfo <FedID> - Get detailed information about a federation using the federation ID.",
        "ban": "/ban <user> <reason> - Ban a user from the federation with an optional reason.",
        "unban": "/unban <user> - Unban a user from the federation.",
        "banlist": "/banlist - List all banned users in the federation.",
        "whitelist": "/whitelist <user> - Add a user to the federation's whitelist.",
        "unwhitelist": "/unwhitelist <user> - Remove a user from the federation's whitelist.",
        "whitelistlist": "/whitelistlist - List all whitelisted users in the federation.",
        "warn": "/warn <user> <reason> - Warn a user with an optional reason.",
        "unwarn": "/unwarn <user> - Remove a warning from a user.",
        "warnlist": "/warnlist - List all warned users in the federation.",
        "kick": "/kick <user> - Kick a user from the group.",
        "promote": "/promote <user> - Promote a user to admin.",
        "demote": "/demote <user> - Demote an admin to a regular user.",
        "mute": "/mute <user> - Mute a user in the group.",
        "unmute": "/unmute <user> - Unmute a user in the group."
    }
    
    if command in detailed_help_texts:
        await update.message.reply_text(detailed_help_texts[command])
    else:
        await update.message.reply_text("No detailed help available for this command.")

def register_help_handlers(app):
    app.add_handler(CommandHandler("help", help_menu))
    app.add_handler(CommandHandler("help", detailed_help, pass_args=True))

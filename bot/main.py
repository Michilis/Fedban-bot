import sys
import os
import asyncio
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from bot.app import bot  # Import the bot instance
from bot.db import init_db
import bot.commands
import bot.callbacks

async def main():
    await init_db()
    
    updater = Updater(bot=bot, use_context=True)

    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", bot.commands.start))
    dp.add_handler(CommandHandler("fedhelp", bot.commands.fedhelp))
    dp.add_handler(CommandHandler("newfed", bot.commands.new_fed))
    dp.add_handler(CommandHandler("delfed", bot.commands.del_fed))
    dp.add_handler(CommandHandler("fedtransfer", bot.commands.fed_transfer))
    dp.add_handler(CommandHandler("myfeds", bot.commands.my_feds))
    dp.add_handler(CommandHandler("renamefed", bot.commands.rename_fed))
    dp.add_handler(CommandHandler(["setfedlog", "unsetfedlog"], bot.commands.set_unset_fed_log))
    dp.add_handler(CommandHandler("chatfed", bot.commands.chat_fed))
    dp.add_handler(CommandHandler("joinfed", bot.commands.join_fed))
    dp.add_handler(CommandHandler("leavefed", bot.commands.leave_fed))
    dp.add_handler(CommandHandler("fedchats", bot.commands.fed_chats))
    dp.add_handler(CommandHandler("fedinfo", bot.commands.fed_info))
    dp.add_handler(CommandHandler("fedadmins", bot.commands.fed_admins))
    dp.add_handler(CommandHandler("fpromote", bot.commands.fpromote))
    dp.add_handler(CommandHandler("fdemote", bot.commands.fdemote))
    dp.add_handler(CommandHandler(["fban", "sfban"], bot.commands.fban_user))
    dp.add_handler(CommandHandler(["unfban", "sunfban"], bot.commands.funban_user))
    dp.add_handler(CommandHandler("fedstat", bot.commands.fed_stat))
    dp.add_handler(CommandHandler("fbroadcast", bot.commands.fbroadcast_message))

    dp.add_handler(CallbackQueryHandler(bot.callbacks.fed_admin_commands, pattern="^fed_admin$"))
    dp.add_handler(CallbackQueryHandler(bot.callbacks.fed_owner_commands, pattern="^fed_owner$"))
    dp.add_handler(CallbackQueryHandler(bot.callbacks.user_commands, pattern="^user$"))
    dp.add_handler(CallbackQueryHandler(bot.callbacks.back_to_main, pattern="^back_to_main$"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    asyncio.run(main())

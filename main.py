import asyncio
from pyrogram import Client
from config import Config
from modules import federation, help

app = Client(
    "fedban_bot",
    bot_token=Config.BOT_TOKEN
)

# Registering handlers from modules
app.add_handler(filters.command("help"), help.help_menu)
app.add_handler(filters.callback_query("fed_admin_commands"), help.fed_admin_commands)
app.add_handler(filters.callback_query("federation_owner_commands"), help.federation_owner_commands)
app.add_handler(filters.callback_query("user_commands"), help.user_commands)
app.add_handler(filters.callback_query("main_help"), help.main_help)

app.add_handler(filters.command("newfed"), federation.new_fed)
app.add_handler(filters.command("joinfed"), federation.join_fed)
app.add_handler(filters.command("leavefed"), federation.leave_fed)
app.add_handler(filters.command("renamefed"), federation.rename_fed)
app.add_handler(filters.command("fedtransfer"), federation.fed_transfer)
app.add_handler(filters.command("delfed"), federation.del_fed)
app.add_handler(filters.command("setfedlog"), federation.set_fed_log)
app.add_handler(filters.command("unsetfedlog"), federation.unset_fed_log)
app.add_handler(filters.command("fpromote"), federation.fed_promote)
app.add_handler(filters.command("fdemote"), federation.fed_demote)
app.add_handler(filters.command("fban"), federation.fed_ban)
app.add_handler(filters.command("sfban"), federation.sfed_ban)
app.add_handler(filters.command("unfban"), federation.fed_unban)
app.add_handler(filters.command("sunfban"), federation.sfed_unban)
app.add_handler(filters.command("fedinfo"), federation.fed_info)
app.add_handler(filters.command("fedadmins"), federation.fed_admins)
app.add_handler(filters.command("fedchats"), federation.fed_chats)
app.add_handler(filters.command("fedstat"), federation.fed_stat)
app.add_handler(filters.command("fbroadcast"), federation.fbroadcast)

if __name__ == "__main__":
    app.run()

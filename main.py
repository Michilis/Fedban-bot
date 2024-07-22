from pyrogram import Client, filters
from config import Config
from modules import federation, help

app = Client("fedban_bot", bot_token=Config.BOT_TOKEN)

# Initialize the database
@app.on_startup
async def on_startup():
    await federation.init_db()

# Add handlers for federation commands
app.add_handler(filters.command("newfed"), federation.new_fed)
app.add_handler(filters.command("joinfed"), federation.join_fed)
app.add_handler(filters.command("leavefed"), federation.leave_fed)
app.add_handler(filters.command("renamefed"), federation.rename_fed)

# Add handler for help command
app.add_handler(filters.command("help"), help.help_menu)

# Register help menu handlers
help.register_help_handlers(app)

app.run()

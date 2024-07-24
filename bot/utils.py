import uuid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def generate_fed_id(user_id):
    return f"{user_id}:{uuid.uuid4()}"

def create_confirmation_markup(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data=callback_data)],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])

def extract_user_and_reason(message):
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]
    reason = message.text.split(' ', 2)[2] if len(message.command) > 2 else None
    return user_id, reason

# Add more utility functions as needed

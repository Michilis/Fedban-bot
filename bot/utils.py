import uuid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def generate_fed_id(user_id):
    return f"{user_id}:{uuid.uuid4()}"

def create_confirmation_markup(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data=callback_data)],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])

# Add more utility functions as needed

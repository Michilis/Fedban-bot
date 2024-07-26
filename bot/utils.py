import uuid
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db import get_fed_info
from app import app

async def generate_fed_id(user_id):
    return f"{user_id}:{uuid.uuid4()}"

def create_confirmation_markup(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data=callback_data)],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])

def extract_user_and_reason(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else None
    else:
        args = message.text.split()
        user_id = int(args[1])
        reason = " ".join(args[2:]) if len(args) > 2 else None
    return user_id, reason

async def is_group_admin(chat_id, user_id):
    member = await app.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

async def is_user_fed_owner(fed_id, user_id):
    fed_info = await get_fed_info(fed_id)
    return fed_info and fed_info["owner_id"] == user_id

async def check_banned_user(fed_id, user_id):
    fed_info = await get_fed_info(fed_id)
    for banned_user in fed_info.get("banned_users", []):
        if banned_user["user_id"] == user_id:
            return banned_user
    return None

async def chat_id_and_names_in_fed(fed_id):
    fed_info = await get_fed_info(fed_id)
    chat_ids = fed_info.get("chat_ids", [])
    chat_names = []
    for chat_id in chat_ids:
        chat = await app.get_chat(chat_id)
        chat_names.append(chat.title)
    return chat_ids, chat_names

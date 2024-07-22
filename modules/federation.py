import asyncio
import uuid
import asyncpg
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType, ChatMemberStatus
from config import Config

async def init_db():
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS federations (
            fed_id UUID PRIMARY KEY,
            fed_name TEXT,
            created_time TIMESTAMP,
            owner_id BIGINT
        )
    ''')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id BIGINT PRIMARY KEY,
            chat_title TEXT,
            fed_id UUID REFERENCES federations(fed_id)
        )
    ''')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS fedbans (
            fed_id UUID REFERENCES federations(fed_id),
            user_id BIGINT,
            reason TEXT,
            PRIMARY KEY (fed_id, user_id)
        )
    ''')
    await conn.close()

async def new_fed_db(fed_name, fed_id, created_time, owner_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        INSERT INTO federations (fed_id, fed_name, created_time, owner_id) VALUES ($1, $2, $3, $4)
    ''', fed_id, fed_name, created_time, owner_id)
    await conn.close()

async def join_fed_db(chat_id, chat_title, fed_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        INSERT INTO chats (chat_id, chat_title, fed_id) VALUES ($1, $2, $3)
    ''', chat_id, chat_title, fed_id)
    await conn.close()

async def leave_fed_db(chat_id, chat_title, fed_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        DELETE FROM chats WHERE chat_id=$1 AND fed_id=$2
    ''', chat_id, fed_id)
    await conn.close()

async def rename_fed_db(owner_id, fed_name):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        UPDATE federations SET fed_name=$1 WHERE owner_id=$2
    ''', fed_name, owner_id)
    await conn.close()

async def get_fed_name(fed_id=None, owner_id=None):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    if fed_id:
        row = await conn.fetchrow('''
            SELECT fed_name FROM federations WHERE fed_id=$1
        ''', fed_id)
    else:
        row = await conn.fetchrow('''
            SELECT fed_name FROM federations WHERE owner_id=$1
        ''', owner_id)
    await conn.close()
    return row['fed_name'] if row else None

async def get_fed_info(fed_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    row = await conn.fetchrow('''
        SELECT * FROM federations WHERE fed_id=$1
    ''', fed_id)
    await conn.close()
    return row

async def get_fed_admins(fed_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    rows = await conn.fetch('''
        SELECT owner_id FROM federations WHERE fed_id=$1
    ''', fed_id)
    await conn.close()
    return [row['owner_id'] for row in rows]

async def get_connected_chats(fed_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    rows = await conn.fetch('''
        SELECT chat_id FROM chats WHERE fed_id=$1
    ''', fed_id)
    await conn.close()
    return [row['chat_id'] for row in rows]

async def is_fed_exist(fed_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    row = await conn.fetchrow('''
        SELECT fed_id FROM federations WHERE fed_id=$1
    ''', fed_id)
    await conn.close()
    return bool(row)

async def is_user_fban(fed_id, user_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    row = await conn.fetchrow('''
        SELECT user_id FROM fedbans WHERE fed_id=$1 AND user_id=$2
    ''', fed_id, user_id)
    await conn.close()
    return bool(row)

async def get_fed_reason(fed_id, user_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    row = await conn.fetchrow('''
        SELECT reason FROM fedbans WHERE fed_id=$1 AND user_id=$2
    ''', fed_id, user_id)
    await conn.close()
    return row['reason'] if row else None

async def update_reason(fed_id, user_id, reason):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        UPDATE fedbans SET reason=$1 WHERE fed_id=$2 AND user_id=$3
    ''', reason, fed_id, user_id)
    await conn.close()

async def user_fban(fed_id, user_id, reason):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        INSERT INTO fedbans (fed_id, user_id, reason) VALUES ($1, $2, $3)
    ''', fed_id, user_id, reason)
    await conn.close()

async def user_unfban(fed_id, user_id):
    conn = await asyncpg.connect(Config.DATABASE_URL)
    await conn.execute('''
        DELETE FROM fedbans WHERE fed_id=$1 AND user_id=$2
    ''', fed_id, user_id)
    await conn.close()

async def new_fed(client, message):
    if message.chat.type == ChatType.PRIVATE:
        if len(message.command) < 2:
            return await message.reply_text("Please write the name of the federation!")
        
        fed_name = message.text.split(None, 1)[1]
        fed_id = str(uuid.uuid4())
        owner_id = message.from_user.id
        created_time = message.date.strftime('%Y-%m-%d %H:%M:%S')
        await new_fed_db(fed_name, fed_id, created_time, owner_id)
        
        await message.reply_text(
            f"**Congrats, you have successfully created a federation!**\n\n"
            f"**Name:** {fed_name}\n"
            f"**ID:** `{fed_id}`\n"
            f"**Creator:** {message.from_user.mention}\n"
            f"**Created Date:** {created_time}\n\n"
            "Use this ID to join federation! eg: `/joinfed {fed_id}`"
        )
        
        await client.send_message(
            Config.LOG_GROUP_ID,
            f"**New Federation created with FedID:**\n\n"
            f"**Name:** {fed_name}\n"
            f"**ID:** `{fed_id}`\n"
            f"**Creator:** {message.from_user.mention}\n"
            f"**Created Date:** {created_time}"
        )

async def join_fed(client, message):
    chat_id = message.chat.id
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply_text("Only supergroups can join feds.")
    
    if len(message.command) < 2:
        return await message.reply_text("You need to specify which federation you're asking about by giving me a FedID!")
    
    fed_id = message.command[1]
    if not await is_fed_exist(fed_id):
        return await message.reply_text("This FedID does not refer to an existing federation.")
    
    st = await client.get_chat_member(chat_id, user_id)
    if st.status != ChatMemberStatus.OWNER:
        return await message.reply_text("Only Group Creator can join new fed!")
    
    chat_title = message.chat.title
    await join_fed_db(chat_id, chat_title, fed_id)
    fed_name = await get_fed_name(fed_id=fed_id)
    
    await message.reply_text(f'Successfully joined the "{fed_name}" federation!')

async def leave_fed(client, message):
    chat_id = message.chat.id
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("You need to specify which federation you're asking about by giving me a FedID!")
    
    fed_id = message.command[1]
    if not await is_fed_exist(fed_id):
        return await message.reply_text("This FedID does not refer to an existing federation.")
    
    st = await client.get_chat_member(chat_id, user_id)
    if st.status != ChatMemberStatus.OWNER:
        return await message.reply_text("Only Group Creator can leave fed!")
    
    chat_title = message.chat.title
    await leave_fed_db(chat_id, chat_title, fed_id)
    fed_name = await get_fed_name(fed_id=fed_id)
    
    await message.reply_text(f'Successfully left the "{fed_name}" federation!')

async def rename_fed(client, message):
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text("You can only rename your fed in PM.")
    
    if len(message.command) < 2:
        return await message.reply_text("You need to give your federation a name! Federation names can be up to 64 characters long.")
    
    fed_name = ' '.join(message.command[1:])
    if len(fed_name) > 60:
        return await message.reply_text("Your fed must be smaller than 60 words.")
    
    owner_id = message.from_user.id
    fed_id = await get_fed_from_ownerid(owner_id)
    if fed_id is None:
        return await message.reply_text("It doesn't look like you have a federation yet!")
    
    old_fed_name = await get_fed_name(owner_id=owner_id)
    await rename_fed_db(owner_id, fed_name)
    
    await message.reply_text(f"I've renamed your federation from '{old_fed_name}' to '{fed_name}'. ( FedID: `{fed_id}`.)")
    
    connected_chats = await get_connected_chats(fed_id)
    for chat_id in connected_chats:
        await client.send_message(
            chat_id,
            f"**Federation renamed**\n"
            f"**Old fed name:** {old_fed_name}\n"
            f"**New fed name:** {fed_name}\n"
            f"FedID: `{fed_id}`"
        )

# Additional federation functions should be implemented here...

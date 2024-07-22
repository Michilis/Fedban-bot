import asyncpg
import uuid
import time
import html
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client

# Database connection
async def init_db(database_url):
    global conn
    conn = await asyncpg.connect(database_url)

# Database functions
async def is_fed_exist(fed_id):
    return await conn.fetchval("SELECT EXISTS(SELECT 1 FROM federations WHERE fed_id=$1)", fed_id)

async def get_fed_name(fed_id):
    return await conn.fetchval("SELECT fed_name FROM federations WHERE fed_id=$1", fed_id)

async def join_fed_db(chat_id, chat_title, fed_id):
    await conn.execute("INSERT INTO chat_feds (chat_id, chat_title, fed_id) VALUES ($1, $2, $3)", chat_id, chat_title, fed_id)

async def leave_fed_db(chat_id, chat_title, fed_id):
    await conn.execute("DELETE FROM chat_feds WHERE chat_id=$1 AND fed_id=$2", chat_id, fed_id)

async def get_connected_chats(fed_id):
    return await conn.fetch("SELECT chat_id FROM chat_feds WHERE fed_id=$1", fed_id)

async def new_fed_db(fed_name, fed_id, created_time, owner_id):
    await conn.execute("INSERT INTO federations (fed_name, fed_id, created_time, owner_id) VALUES ($1, $2, $3, $4)", fed_name, fed_id, created_time, owner_id)

async def get_fed_from_chat(chat_id):
    return await conn.fetchval("SELECT fed_id FROM chat_feds WHERE chat_id=$1", chat_id)

async def is_user_fban(fed_id, user_id):
    return await conn.fetchval("SELECT EXISTS(SELECT 1 FROM fed_bans WHERE fed_id=$1 AND user_id=$2)", fed_id, user_id)

async def get_fed_reason(fed_id, user_id):
    return await conn.fetchval("SELECT reason FROM fed_bans WHERE fed_id=$1 AND user_id=$2", fed_id, user_id)

async def get_fed_owner(fed_id):
    return await conn.fetchval("SELECT owner_id FROM federations WHERE fed_id=$1", fed_id)

async def get_fed_admins(fed_id):
    return await conn.fetch("SELECT user_id FROM fed_admins WHERE fed_id=$1", fed_id)

async def get_fed_from_ownerid(owner_id):
    return await conn.fetchval("SELECT fed_id FROM federations WHERE owner_id=$1", owner_id)

async def update_reason(fed_id, user_id, reason):
    await conn.execute("UPDATE fed_bans SET reason=$1 WHERE fed_id=$2 AND user_id=$3", reason, fed_id, user_id)

async def user_fban(fed_id, user_id, reason):
    await conn.execute("INSERT INTO fed_bans (fed_id, user_id, reason) VALUES ($1, $2, $3)", fed_id, user_id, reason)

async def user_unfban(fed_id, user_id):
    await conn.execute("DELETE FROM fed_bans WHERE fed_id=$1 AND user_id=$2", fed_id, user_id)

async def fed_rename_db(owner_id, fed_name):
    await conn.execute("UPDATE federations SET fed_name=$1 WHERE owner_id=$2", fed_name, owner_id)

# Federation commands
async def new_fed(client, message):
    if message.chat.type == 'supergroup':
        return await message.reply('Create your federation in my PM - not in a group.')
    if len(message.command) < 2:
        return await message.reply("Give your federation a name!")
    if len(' '.join(message.command[1:])) > 60:
        return await message.reply("Your fed must be smaller than 60 words.")
    
    fed_name = ' '.join(message.command[1:])
    fed_id = str(uuid.uuid4())
    owner_id = message.from_user.id
    uname = message.from_user.mention
    created_time = time.ctime()

    await new_fed_db(fed_name, fed_id, created_time, owner_id)
    await message.reply(f"""
<b>Congrats, you have successfully created a federation</b>

<b>Name:</b> {fed_name}
<b>ID:</b> <code>{fed_id}</code>
<b>Creator:</b> {uname}
<b>Created Date</b>: {created_time}

Use this ID to join federation! eg:<code> /joinfed {fed_id}</code>""")
    await client.send_message(chat_id=int(os.getenv("LOG_GROUP_ID")), text=(f"""
<b>New Federation created with FedID:</b>

<b>Name:</b> {fed_name}
<b>ID:</b> <code>{fed_id}</code>
<b>Creator:</b> {uname}
<b>Created Date</b>: {created_time}"""))

async def join_fed(client, message):
    group_id = message.chat.id
    userid = message.from_user.id if message.from_user else None
    if message.chat.type != 'supergroup':
        return await message.reply("Only supergroups can join feds.")
    if len(message.command) < 2:
        return await message.reply("You need to specify which federation you're asking about by giving me a FedID!")
    st = await client.get_chat_member(group_id, userid)
    if st.status != "creator":
        return await message.reply("Only Group Creator can join new fed!")
    if not await is_fed_exist(message.command[1]):
        return await message.reply("This FedID does not refer to an existing federation.")
    
    fed_id = message.command[1]
    chat_id = message.chat.id
    chat_title = html.escape(message.chat.title)
    fed_name = await get_fed_name(fed_id)
    await join_fed_db(chat_id, chat_title, fed_id)
    await message.reply(f'Successfully joined the "{fed_name}" federation!')

async def leave_fed(client, message):
    group_id = message.chat.id
    userid = message.from_user.id if message.from_user else None
    if len(message.command) < 2:
        return await message.reply("You need to specify which federation you're asking about by giving me a FedID!")
    st = await client.get_chat_member(group_id, userid)
    if st.status != "creator":
        return await message.reply("Only Group Creator can leave fed!")
    if not await is_fed_exist(message.command[1]):
        return await message.reply("This FedID does not refer to an existing federation.")
    
    fed_id = message.command[1]
    chat_id = message.chat.id
    chat_title = html.escape(message.chat.title)
    fed_name = await get_fed_name(fed_id)
    await leave_fed_db(chat_id, chat_title, fed_id)
    await message.reply(f'Successfully left the "{fed_name}" federation!')

async def info_feds(client, message):
    if len(message.command) < 2:
        return await message.reply("You need to specify which federation you're asking about by giving me a FedID!")
    if not await is_fed_exist(message.command[1]):
        return await message.reply("This FedID does not refer to an existing federation.")
    
    fed_id = message.command[1]
    name = await get_fed_name(fed_id)
    chats = await get_connected_chats(fed_id)
    await message.reply(f"""
<b>Federation info</b>
<b>Name:</b> {name}
<b>ID:</b> <code>{fed_id}</code>
<b>Chats in the fed:</b> {len(chats)}""")

async def rename_fed(client, message):
    owner_id = message.from_user.id
    if message.chat.type != 'private':
        return await message.reply("You can only rename your fed in PM.")
    if len(message.command) < 2:
        return await message.reply("You need to give your federation a name! Federation names can be up to 64 characters long.")
    if len(' '.join(message.command[1:])) > 60:
        return await message.reply("Your fed must be smaller than 60 words.")
    
    fed_id = await get_fed_from_ownerid(owner_id)
    if fed_id is None:
        return await message.reply("It doesn't look like you have a federation yet!")
    
    fed_name = ' '.join(message.command[1:])
    old_fed_name = await get_fed_name(fed_id)
    await fed_rename_db(owner_id, fed_name)
    await message.reply(f"I've renamed your federation from '{old_fed_name}' to '{fed_name}'. (FedID: `{fed_id}`.)")
    
    connected_chats = await get_connected_chats(fed_id)
    for chat_id in connected_chats:
        await client.send_message(chat_id=chat_id, text=(
            "**Federation renamed**\n"
            f"**Old fed name:** {old_fed_name}\n"
            f"**New fed name:** {fed_name}\n"
            f"FedID: `{fed_id}`"))

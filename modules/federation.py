import uuid
import time
import asyncpg
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

pool = None
LOG_GROUP_ID = None

async def init_db(database_url):
    global pool
    pool = await asyncpg.create_pool(database_url)
    
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS federations (
                fed_id UUID PRIMARY KEY,
                fed_name TEXT NOT NULL,
                owner_id BIGINT NOT NULL,
                created_time TIMESTAMP DEFAULT NOW()
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS federation_chats (
                chat_id BIGINT PRIMARY KEY,
                chat_title TEXT NOT NULL,
                fed_id UUID REFERENCES federations(fed_id)
            )
        ''')

async def new_fed(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type != 'private':
        await update.message.reply_text('Create your federation in my PM - not in a group.')
        return
    if len(context.args) < 1:
        await update.message.reply_text('Give your federation a name!')
        return
    fed_name = ' '.join(context.args)
    fed_id = str(uuid.uuid4())
    owner_id = update.message.from_user.id
    uname = update.message.from_user.mention_html()
    created_time = time.ctime()

    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO federations (fed_id, fed_name, owner_id, created_time)
            VALUES ($1, $2, $3, $4)
        ''', fed_id, fed_name, owner_id, created_time)

    await update.message.reply_text(f'''
<b>Congrats, you have successfully created a federation </b>

<b>Name:</b> {fed_name}
<b>ID:</b> <code>{fed_id}</code>
<b>Creator:</b> {uname}     
<b>Created Date:</b> {created_time}

Use this ID to join federation! eg:<code> /joinfed {fed_id}</code>''', parse_mode='HTML')

    await context.bot.send_message(chat_id=LOG_GROUP_ID, text=f'''
<b>New Federation created with FedID:</b>

<b>Name:</b> {fed_name}
<b>ID:</b> <code>{fed_id}</code>
<b>Creator:</b> {uname}     
<b>Created Date:</b> {created_time}''', parse_mode='HTML')

async def join_fed(update: Update, context: CallbackContext) -> None:
    group_id = update.message.chat_id
    userid = update.message.from_user.id
    if update.message.chat.type != 'supergroup':
        await update.message.reply_text("Only supergroups can join feds.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("You need to specify which federation you're asking about by giving me a FedID!")
        return
    chat_member = await context.bot.get_chat_member(group_id, userid)
    if chat_member.status != "creator":
        await update.message.reply_text("Only Group Creator can join new fed!")
        return
    fed_id = context.args[0]

    async with pool.acquire() as conn:
        fed_exists = await conn.fetchval('SELECT 1 FROM federations WHERE fed_id = $1', fed_id)
        if not fed_exists:
            await update.message.reply_text("This FedID does not refer to an existing federation.")
            return

        chat_title = update.message.chat.title
        await conn.execute('''
            INSERT INTO federation_chats (chat_id, chat_title, fed_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (chat_id) DO UPDATE
            SET chat_title = EXCLUDED.chat_title, fed_id = EXCLUDED.fed_id
        ''', group_id, chat_title, fed_id)

    fed_name = await conn.fetchval('SELECT fed_name FROM federations WHERE fed_id = $1', fed_id)
    await update.message.reply_text(f'Successfully joined the "{fed_name}" federation!')

async def leave_fed(update: Update, context: CallbackContext) -> None:
    group_id = update.message.chat_id
    userid = update.message.from_user.id
    if len(context.args) < 1:
        await update.message.reply_text("You need to specify which federation you're asking about by giving me a FedID!")
        return
    chat_member = await context.bot.get_chat_member(group_id, userid)
    if chat_member.status != "creator":
        await update.message.reply_text("Only Group Creator can leave fed!")
        return
    fed_id = context.args[0]

    async with pool.acquire() as conn:
        fed_exists = await conn.fetchval('SELECT 1 FROM federations WHERE fed_id = $1', fed_id)
        if not fed_exists:
            await update.message.reply_text("This FedID does not refer to an existing federation.")
            return

        await conn.execute('DELETE FROM federation_chats WHERE chat_id = $1 AND fed_id = $2', group_id, fed_id)
        fed_name = await conn.fetchval('SELECT fed_name FROM federations WHERE fed_id = $1', fed_id)
        await update.message.reply_text(f'Successfully left the "{fed_name}" federation!')

async def rename_fed(update: Update, context: CallbackContext) -> None:
    owner_id = update.message.from_user.id
    if update.message.chat.type != 'private':
        await update.message.reply_text("You can only rename your fed in PM.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("You need to give your federation a name! Federation names can be up to 64 characters long.")
        return
    fed_name = ' '.join(context.args)

    async with pool.acquire() as conn:
        fed_id = await conn.fetchval('SELECT fed_id FROM federations WHERE owner_id = $1', owner_id)
        if not fed_id:
            await update.message.reply_text("It doesn't look like you have a federation yet!")
            return

        old_fed_name = await conn.fetchval('SELECT fed_name FROM federations WHERE fed_id = $1', fed_id)
        await conn.execute('UPDATE federations SET fed_name = $1 WHERE fed_id = $2', fed_name, fed_id)

    await update.message.reply_text(f"I've renamed your federation from '{old_fed_name}' to '{fed_name}'. ( FedID: `{fed_id}`.)")

    async with pool.acquire() as conn:
        connected_chats = await conn.fetch('SELECT chat_id FROM federation_chats WHERE fed_id = $1', fed_id)
        for chat in connected_chats:
            await context.bot.send_message(
                chat_id=chat['chat_id'], text=(
                    "**Federation renamed**\n"
                    f"**Old fed name:** {old_fed_name}\n"
                    f"**New fed name:** {fed_name}\n"
                    f"FedID: `{fed_id}`"))

async def info_feds(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("You need to specify which federation you're asking about by giving me a FedID!")
        return
    fed_id = context.args[0]

    async with pool.acquire() as conn:
        fed_exists = await conn.fetchval('SELECT 1 FROM federations WHERE fed_id = $1', fed_id)
        if not fed_exists:
            await update.message.reply_text("This FedID does not refer to an existing federation.")
            return

        fed_name = await conn.fetchval('SELECT fed_name FROM federations WHERE fed_id = $1', fed_id)
        chats = await conn.fetch('SELECT chat_id FROM federation_chats WHERE fed_id = $1', fed_id)

    await update.message.reply_text(f'''
<b>Federation info</b>
<b>Name:</b> {fed_name}
<b>ID:</b> <code>{fed_id}</code>
<b>Chats in the fed:</b> {len(chats)}''', parse_mode='HTML')

# Register federation handlers
def register_federation_handlers(app):
    app.add_handler(CommandHandler("newfed", new_fed))
    app.add_handler(CommandHandler("joinfed", join_fed))
    app.add_handler(CommandHandler("leavefed", leave_fed))
    app.add_handler(CommandHandler("renamefed", rename_fed))
    app.add_handler(CommandHandler("fedinfo", info_feds))

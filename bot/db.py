import asyncpg
from config import DATABASE_URL

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS federations (
            fed_id VARCHAR PRIMARY KEY,
            fed_name VARCHAR,
            owner_id BIGINT,
            fadmins JSONB,
            owner_mention VARCHAR,
            banned_users JSONB,
            chat_ids JSONB,
            log_group_id BIGINT
        );
    ''')
    await conn.close()

async def get_conn():
    return await asyncpg.connect(DATABASE_URL)

async def create_federation(fed_id, fed_name, owner_id, owner_mention, log_group_id):
    conn = await get_conn()
    await conn.execute('''
        INSERT INTO federations (fed_id, fed_name, owner_id, fadmins, owner_mention, banned_users, chat_ids, log_group_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    ''', fed_id, fed_name, owner_id, [], owner_mention, [], [], log_group_id)
    await conn.close()

async def delete_federation(fed_id):
    conn = await get_conn()
    await conn.execute('DELETE FROM federations WHERE fed_id = $1', fed_id)
    await conn.close()

async def get_fed_info(fed_id):
    conn = await get_conn()
    row = await conn.fetchrow('SELECT * FROM federations WHERE fed_id = $1', fed_id)
    await conn.close()
    return row

async def get_feds_by_owner(owner_id):
    conn = await get_conn()
    rows = await conn.fetch('SELECT * FROM federations WHERE owner_id = $1', owner_id)
    await conn.close()
    return rows

async def add_fed_admin(fed_id, user_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET fadmins = array_append(fadmins, $1) WHERE fed_id = $2
    ''', user_id, fed_id)
    await conn.close()

async def remove_fed_admin(fed_id, user_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET fadmins = array_remove(fadmins, $1) WHERE fed_id = $2
    ''', user_id, fed_id)
    await conn.close()

async def add_banned_user(fed_id, user_id, reason):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET banned_users = array_append(banned_users, $1) WHERE fed_id = $2
    ''', {'user_id': user_id, 'reason': reason}, fed_id)
    await conn.close()

async def remove_banned_user(fed_id, user_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET banned_users = array_remove(banned_users, $1) WHERE fed_id = $2
    ''', user_id, fed_id)
    await conn.close()

# Add more database functions as needed

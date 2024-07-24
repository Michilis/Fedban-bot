import asyncpg
from config import DATABASE_URL

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS federations (
            fed_id VARCHAR PRIMARY KEY,
            fed_name VARCHAR,
            owner_id BIGINT,
            fadmins BIGINT[],
            owner_mention VARCHAR,
            banned_users JSONB,
            chat_ids BIGINT[],
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
    banned_user = {'user_id': user_id, 'reason': reason}
    await conn.execute('''
        UPDATE federations SET banned_users = array_append(banned_users, $1) WHERE fed_id = $2
    ''', banned_user, fed_id)
    await conn.close()

async def remove_banned_user(fed_id, user_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET banned_users = array_remove(banned_users, $1) WHERE fed_id = $2
    ''', user_id, fed_id)
    await conn.close()

async def set_log_chat(fed_id, log_group_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET log_group_id = $1 WHERE fed_id = $2
    ''', log_group_id, fed_id)
    await conn.close()

async def get_fed_id(chat_id):
    conn = await get_conn()
    row = await conn.fetchrow('SELECT fed_id FROM federations WHERE $1 = ANY(chat_ids)', chat_id)
    await conn.close()
    return row['fed_id'] if row else None

async def is_user_fed_owner(fed_id, user_id):
    conn = await get_conn()
    row = await conn.fetchrow('SELECT 1 FROM federations WHERE fed_id = $1 AND owner_id = $2', fed_id, user_id)
    await conn.close()
    return bool(row)

async def check_banned_user(fed_id, user_id):
    conn = await get_conn()
    row = await conn.fetchrow('SELECT 1 FROM federations WHERE fed_id = $1 AND $2 = ANY(banned_users)', fed_id, user_id)
    await conn.close()
    return bool(row)

async def chat_join_fed(fed_id, chat_title, chat_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET chat_ids = array_append(chat_ids, $1) WHERE fed_id = $2
    ''', chat_id, fed_id)
    await conn.close()

async def chat_leave_fed(chat_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET chat_ids = array_remove(chat_ids, $1) WHERE $1 = ANY(chat_ids)
    ''', chat_id)
    await conn.close()

async def search_fed_by_id(fed_id):
    return await get_fed_info(fed_id)

async def is_group_admin(chat_id, user_id):
    conn = await get_conn()
    row = await conn.fetchrow('SELECT 1 FROM federations WHERE $1 = ANY(chat_ids) AND (owner_id = $2 OR $2 = ANY(fadmins))', chat_id, user_id)
    await conn.close()
    return bool(row)

async def chat_id_and_names_in_fed(fed_id):
    conn = await get_conn()
    rows = await conn.fetch('SELECT chat_ids FROM federations WHERE fed_id = $1', fed_id)
    await conn.close()
    return rows[0]['chat_ids'], []  # You might need to get chat names separately

async def transfer_owner(fed_id, current_owner_id, new_owner_id):
    conn = await get_conn()
    await conn.execute('''
        UPDATE federations SET owner_id = $1, fadmins = array_append(fadmins, $2) WHERE fed_id = $3 AND owner_id = $4
    ''', new_owner_id, current_owner_id, fed_id, current_owner_id)
    await conn.close()

async def get_user_fstatus(user_id):
    conn = await get_conn()
    rows = await conn.fetch('SELECT fed_id, fed_name FROM federations WHERE $1 = ANY(banned_users)', user_id)
    await conn.close()
    return [{'fed_id': row['fed_id'], 'fed_name': row['fed_name']} for row in rows]

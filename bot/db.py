import asyncpg
from config import DATABASE_URL

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS federations (
            fed_id TEXT PRIMARY KEY,
            fed_name TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            owner_mention TEXT NOT NULL,
            log_group_id INTEGER,
            fadmins JSONB NOT NULL DEFAULT '[]'
        )
    ''')
    await conn.close()

async def create_federation(fed_id, fed_name, owner_id, owner_mention, log_group_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO federations (fed_id, fed_name, owner_id, owner_mention, log_group_id)
        VALUES ($1, $2, $3, $4, $5)
    ''', fed_id, fed_name, owner_id, owner_mention, log_group_id)
    await conn.close()

async def delete_federation(fed_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        DELETE FROM federations WHERE fed_id = $1
    ''', fed_id)
    await conn.close()

async def get_federation(fed_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow('''
        SELECT * FROM federations WHERE fed_id = $1
    ''', fed_id)
    await conn.close()
    return row

async def rename_federation(fed_id, new_name):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        UPDATE federations SET fed_name = $1 WHERE fed_id = $2
    ''', new_name, fed_id)
    await conn.close()

async def transfer_federation(fed_id, new_owner_id, new_owner_mention):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        UPDATE federations SET owner_id = $1, owner_mention = $2 WHERE fed_id = $3
    ''', new_owner_id, new_owner_mention, fed_id)
    await conn.close()

async def get_user_federations(owner_id):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch('''
        SELECT * FROM federations WHERE owner_id = $1
    ''', owner_id)
    await conn.close()
    return rows

async def set_federation_log_channel(fed_id, log_group_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        UPDATE federations SET log_group_id = $1 WHERE fed_id = $2
    ''', log_group_id, fed_id)
    await conn.close()

async def unset_federation_log_channel(fed_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        UPDATE federations SET log_group_id = NULL WHERE fed_id = $1
    ''', fed_id)
    await conn.close()

async def add_federation_admin(fed_id, user_id, user_mention):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        UPDATE federations SET fadmins = jsonb_set(fadmins, '{-1}', $1, true)
        WHERE fed_id = $2
    ''', [{"id": user_id, "mention": user_mention}], fed_id)
    await conn.close()

async def remove_federation_admin(fed_id, user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    fed = await get_federation(fed_id)
    if fed:
        fadmins = fed["fadmins"]
        updated_fadmins = [admin for admin in fadmins if admin["id"] != user_id]
        await conn.execute('''
            UPDATE federations SET fadmins = $1 WHERE fed_id = $2
        ''', updated_fadmins, fed_id)
    await conn.close()

async def get_federation_admins(fed_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow('''
        SELECT fadmins FROM federations WHERE fed_id = $1
    ''', fed_id)
    await conn.close()
    return row["fadmins"] if row else []

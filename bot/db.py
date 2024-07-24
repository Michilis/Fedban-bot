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
        -- Add more tables as needed
    ''')
    await conn.close()

async def get_conn():
    return await asyncpg.connect(DATABASE_URL)

# Add database functions here
# Example: fetch federations, add federation, update federation, etc.

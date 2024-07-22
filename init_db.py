import asyncpg
import os

async def init_db():
    database_url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(database_url)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS federations (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    await conn.close()

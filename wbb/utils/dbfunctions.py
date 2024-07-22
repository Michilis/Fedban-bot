import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def create_federation(owner_id, name):
    pool = await create_pool()
    async with pool.acquire() as connection:
        federation_id = await connection.fetchval(
            "INSERT INTO federations (owner_id, name) VALUES ($1, $2) RETURNING id",
            owner_id, name
        )
    return federation_id

async def delete_federation(federation_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute("DELETE FROM federations WHERE id = $1", federation_id)

async def get_federations(owner_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        return await connection.fetch("SELECT * FROM federations WHERE owner_id = $1", owner_id)

async def get_federation_info(federation_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        return await connection.fetchrow("SELECT * FROM federations WHERE id = $1", federation_id)

async def add_group_to_federation(federation_id, chat_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute("INSERT INTO federation_groups (federation_id, chat_id) VALUES ($1, $2)", federation_id, chat_id)

async def remove_group_from_federation(federation_id, chat_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute("DELETE FROM federation_groups WHERE federation_id = $1 AND chat_id = $2", federation_id, chat_id)

async def add_fedban_user(federation_id, user_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute("INSERT INTO federation_bans (federation_id, user_id) VALUES ($1, $2)", federation_id, user_id)

async def remove_fedban_user(federation_id, user_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute("DELETE FROM federation_bans WHERE federation_id = $1 AND user_id = $2", federation_id, user_id)

async def is_user_fedbanned(federation_id, user_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        return await connection.fetchval("SELECT 1 FROM federation_bans WHERE federation_id = $1 AND user_id = $2", federation_id, user_id)

async def get_groups_in_federation(federation_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        return await connection.fetch("SELECT chat_id FROM federation_groups WHERE federation_id = $1", federation_id)

async def transfer_federation_ownership(federation_id, new_owner_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute("UPDATE federations SET owner_id = $1 WHERE id = $2", new_owner_id, federation_id)

async def update_federation_name(federation_id, new_name):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute("UPDATE federations SET name = $1 WHERE id = $2", new_name, federation_id)

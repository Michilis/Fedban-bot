import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Federation-related database functions

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
        await connection.execute(
            "DELETE FROM federations WHERE id = $1",
            federation_id
        )

async def get_federations(owner_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        federations = await connection.fetch(
            "SELECT id, name FROM federations WHERE owner_id = $1",
            owner_id
        )
    return federations

async def get_federation_info(federation_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        federation = await connection.fetchrow(
            "SELECT * FROM federations WHERE id = $1",
            federation_id
        )
    return federation

async def update_federation_name(federation_id, new_name):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "UPDATE federations SET name = $1 WHERE id = $2",
            new_name, federation_id
        )

async def transfer_federation_ownership(federation_id, new_owner_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "UPDATE federations SET owner_id = $1 WHERE id = $2",
            new_owner_id, federation_id
        )

async def add_group_to_federation(federation_id, group_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO federation_groups (federation_id, group_id) VALUES ($1, $2)",
            federation_id, group_id
        )

async def remove_group_from_federation(federation_id, group_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "DELETE FROM federation_groups WHERE federation_id = $1 AND group_id = $2",
            federation_id, group_id
        )

async def get_groups_in_federation(federation_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        groups = await connection.fetch(
            "SELECT group_id FROM federation_groups WHERE federation_id = $1",
            federation_id
        )
    return [group['group_id'] for group in groups]

async def add_fedban_user(federation_id, user_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO fedbans (federation_id, user_id) VALUES ($1, $2)",
            federation_id, user_id
        )

async def remove_fedban_user(federation_id, user_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "DELETE FROM fedbans WHERE federation_id = $1 AND user_id = $2",
            federation_id, user_id
        )

async def is_user_fedbanned(federation_id, user_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        banned = await connection.fetchrow(
            "SELECT * FROM fedbans WHERE federation_id = $1 AND user_id = $2",
            federation_id, user_id
        )
    return banned is not None

# Karma-related database functions

async def is_karma_on(chat_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        state = await connection.fetchval(
            "SELECT karma_state FROM chats WHERE chat_id = $1",
            chat_id
        )
    return state == "ON"

async def karma_on(chat_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "UPDATE chats SET karma_state = 'ON' WHERE chat_id = $1",
            chat_id
        )

async def karma_off(chat_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "UPDATE chats SET karma_state = 'OFF' WHERE chat_id = $1",
            chat_id
        )

async def get_karma(chat_id, user_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        karma = await connection.fetchrow(
            "SELECT karma FROM karma WHERE chat_id = $1 AND user_id = $2",
            chat_id, user_id
        )
    return karma

async def get_karmas(chat_id):
    pool = await create_pool()
    async with pool.acquire() as connection:
        karmas = await connection.fetch(
            "SELECT user_id, karma FROM karma WHERE chat_id = $1 ORDER BY karma DESC",
            chat_id
        )
    return karmas

async def update_karma(chat_id, user_id, new_karma):
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO karma (chat_id, user_id, karma) VALUES ($1, $2, $3) ON CONFLICT (chat_id, user_id) DO UPDATE SET karma = $3",
            chat_id, user_id, new_karma['karma']
        )

async def alpha_to_int(alpha):
    return int(alpha, 36)

async def int_to_alpha(number):
    return base36encode(number)

def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36 or alphabet[0]

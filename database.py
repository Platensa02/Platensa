import asyncpg
import asyncpg

pool = None

async def init_db(database_url):
    global pool
    pool = await asyncpg.create_pool(database_url)

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            name TEXT,
            role TEXT,
            total_add INTEGER DEFAULT 0,
            total_close INTEGER DEFAULT 0
        )
        """)
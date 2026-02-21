import asyncpg
from config import DATABASE_URL

# Database connection pool yaratish
async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Jadvallarni avtomatik yaratish
async def init_db(pool):
    async with pool.acquire() as conn:

        # Users jadvali
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            full_name TEXT,
            role TEXT
        );
        """)

        # Usage jadvali (ishlatish)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount INT,
            confirmed BOOLEAN DEFAULT FALSE
        );
        """)

        # Payments jadvali (to'lov)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount INT
        );
        """)

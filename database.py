import asyncpg
from config import DATABASE_URL

# Database connection pool
async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Jadval yaratish
async def init_db(pool):
    async with pool.acquire() as conn:

        # Users table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            is_active BOOLEAN DEFAULT FALSE
        );
        """)

        # Usage table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount INT,
            confirmed BOOLEAN DEFAULT FALSE
        );
        """)

        # Payments table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount INT
        );
        """)

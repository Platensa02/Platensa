import asyncpg
from config import DATABASE_URL

# Database pool yaratish
async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Jadvalarni yaratish
async def init_db(pool):
    async with pool.acquire() as conn:

        # 👥 Mijozlar
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            is_active BOOLEAN DEFAULT FALSE
        );
        """)

        # 📦 Ishlatishlar
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount INT,
            confirmed BOOLEAN DEFAULT FALSE
        );
        """)

        # 💰 To‘lovlar
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount INT
        );
        """)

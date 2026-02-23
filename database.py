import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE,
        name TEXT,
        confirmed_amount INTEGER DEFAULT 0,
        payments INTEGER DEFAULT 0
    );
    """)

    await conn.close()
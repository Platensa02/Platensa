import asyncpg
from config import DATABASE_URL

# =========================
# GLOBAL POOL
# =========================
pool: asyncpg.Pool | None = None


# =========================
# CONNECT DATABASE
# =========================
async def connect_db():
    global pool
    pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=1,
        max_size=10
    )


# =========================
# CLOSE DATABASE
# =========================
async def close_db():
    global pool
    if pool:
        await pool.close()


# =========================
# CREATE TABLES
# =========================
async def create_tables():
    async with pool.acquire() as conn:

        # USERS
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # USAGES
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS usages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount INTEGER NOT NULL,
            confirmed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # PAYMENTS
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)


# =========================
# USER FUNCTIONS
# =========================
async def create_user(telegram_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT DO NOTHING",
            telegram_id
        )


async def get_user_by_tg(telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id=$1",
            telegram_id
        )


async def delete_user(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM users WHERE id=$1",
            user_id
        )


async def get_all_active_users():
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM users WHERE is_active=TRUE ORDER BY created_at DESC"
        )


# =========================
# USAGE FUNCTIONS
# =========================
async def create_usage(user_id: int, amount: int):
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO usages (user_id, amount)
            VALUES ($1, $2)
            RETURNING id
        """, user_id, amount)


async def confirm_usage(usage_id: int):
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE usages
            SET confirmed=TRUE
            WHERE id=$1
        """, usage_id)


async def reject_usage(usage_id: int):
    async with pool.acquire() as conn:
        await conn.execute("""
            DELETE FROM usages
            WHERE id=$1
        """, usage_id)


# =========================
# PAYMENT FUNCTIONS
# =========================
async def create_payment(user_id: int, amount: int):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO payments (user_id, amount)
            VALUES ($1, $2)
        """, user_id, amount)


# =========================
# ACCOUNTING
# =========================
async def get_user_stats(user_id: int):
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT
                COALESCE((SELECT SUM(amount)
                          FROM usages
                          WHERE user_id=$1 AND confirmed=TRUE),0) AS used,
                COALESCE((SELECT SUM(amount)
                          FROM payments
                          WHERE user_id=$1),0) AS paid
        """, user_id)

        used = result["used"]
        paid = result["paid"]
        debt = used - paid

        return used, paid, debt
import asyncio
import os
import asyncpg

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_CODE = "1111"
CLIENT_CODE = "2222"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# -------- MEMORY --------
user_state = {}

# -------- DATABASE --------
async def init_db():
    pool = await asyncpg.create_pool(DATABASE_URL)
    dp["pool"] = pool

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            name TEXT,
            role TEXT
        )
        """)

# -------- START --------
@router.message(CommandStart())
async def start(message: Message):
    user_state[message.from_user.id] = "waiting_code"
    await message.answer("Kod kiriting:")

# -------- RUN --------
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
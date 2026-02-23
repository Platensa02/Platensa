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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# -------- KEYBOARDS --------

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Mijozlar")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Statistika")]
        ],
        resize_keyboard=True
    )

# -------- MAIN HANDLER --------

@router.message()
async def main_handler(message: Message):

    user_id = message.from_user.id
    state = user_state.get(user_id)
    pool = dp["pool"]

    # --- KOD BOSQICHI ---
    if state == "waiting_code":

        # ADMIN
        if message.text == ADMIN_CODE:
            user_state[user_id] = "admin"
            await message.answer("Admin panel", reply_markup=admin_menu())
            return

        # CLIENT
        if message.text == CLIENT_CODE:
            user_state[user_id] = "waiting_name"
            await message.answer("Ismingizni yozing:")
            return

        await message.answer("Kod noto‘g‘ri")
        return

    # --- CLIENT NAME BOSQICHI ---
    if state == "waiting_name":

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users(telegram_id, name, role)
                VALUES($1,$2,'client')
                ON CONFLICT (telegram_id)
                DO UPDATE SET name = EXCLUDED.name
                """,
                user_id,
                message.text
            )

        user_state[user_id] = "client"
        await message.answer("Ro‘yxatdan o‘tdingiz ✅", reply_markup=client_menu())
        return

    # --- CLIENT STATISTIKA ---
    if state == "client" and message.text == "Statistika":

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id=$1",
                user_id
            )

        if user:
            await message.answer(
                f"Ism: {user['name']}\n"
                f"Role: {user['role']}"
            )
        else:
            await message.answer("Ma'lumot topilmadi")

        return

    # --- ADMIN MIJOZLAR ---
    if state == "admin" and message.text == "Mijozlar":

        async with pool.acquire() as conn:
            users = await conn.fetch(
                "SELECT * FROM users WHERE role='client'"
            )

        if not users:
            await message.answer("Mijoz yo‘q")
            return

        text = "Mijozlar:\n\n"
        for u in users:
            text += f"{u['id']}. {u['name']}\n"

        await message.answer(text)
        return


# -------- RUN --------
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
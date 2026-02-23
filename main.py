import asyncio
import os
import asyncpg

from aiogram import Bot, Dispatcher, Router
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import CommandStart

# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_CODE = "1111"
CLIENT_CODE = "2222"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ================= MEMORY =================

user_state = {}
selected_user = {}

# ================= DATABASE =================

async def init_db():
    pool = await asyncpg.create_pool(DATABASE_URL)
    dp["pool"] = pool

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

# ================= KEYBOARDS =================

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mijozlar")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Statistika")]
        ],
        resize_keyboard=True
    )

# ================= START =================

@router.message(CommandStart())
async def start(message: Message):
    user_state[message.from_user.id] = "waiting_code"
    await message.answer("Kod kiriting:")

# ================= HANDLER =================

@router.message()
async def handler(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id
    text = message.text
    pool = dp["pool"]
    state = user_state.get(user_id)

    # LOGIN
    if state == "waiting_code":

        if text == ADMIN_CODE:
            user_state[user_id] = "admin"
            await message.answer("Admin panel", reply_markup=admin_menu())
            return

        if text == CLIENT_CODE:
            user_state[user_id] = "waiting_name"
            await message.answer("Ismingizni yozing:")
            return

    # SAVE CLIENT
    if state == "waiting_name":

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users(telegram_id,name,role)
                VALUES($1,$2,'client')
                ON CONFLICT (telegram_id)
                DO UPDATE SET name=EXCLUDED.name
            """, user_id, text)

        user_state[user_id] = "client"
        await message.answer("Ro‘yxatdan o‘tdingiz ✅", reply_markup=client_menu())
        return

    # CLIENT STAT
    if state == "client" and text == "📊 Statistika":

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id=$1",
                user_id
            )

        if user:
            remaining = user["total_add"] - user["total_close"]

            await message.answer(
                f"Qo‘shilgan: {user['total_add']} dona\n"
                f"Yopilgan: {user['total_close']} dona\n"
                f"Qolgan: {remaining} dona"
            )
        return

    # ADMIN LIST
    if state == "admin" and text == "📋 Mijozlar":

        async with pool.acquire() as conn:
            users = await conn.fetch(
                "SELECT * FROM users WHERE role='client'"
            )

        if not users:
            await message.answer("Mijoz yo‘q")
            return

        response = "Mijozlar:\n\n"
        for u in users:
            remaining = u["total_add"] - u["total_close"]
            response += f"ID:{u['id']} | {u['name']} | Qoldiq:{remaining}\n"

        await message.answer(response)
        return

# ================= RUN =================

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import os
import asyncpg

from aiogram import Bot, Dispatcher, Router, F
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
admin_context = {}

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

def admin_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Mijozlar")],
            [KeyboardButton(text="⬅️ Chiqish")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Statistika")],
            [KeyboardButton(text="⬅️ Chiqish")]
        ],
        resize_keyboard=True
    )

def admin_user_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Qo‘shish"), KeyboardButton(text="➖ Yopish")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def confirm_keyboard(action, target_id, amount):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"{action}|yes|{target_id}|{amount}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"{action}|no|{target_id}|{amount}"
                )
            ]
        ]
    )

# ================= START =================

@router.message(CommandStart())
async def start(message: Message):
    user_state[message.from_user.id] = "waiting_code"
    await message.answer("Kod kiriting:")

# ================= MAIN HANDLER =================

@router.message()
async def handler(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id
    pool = dp["pool"]
    state = user_state.get(user_id)

    # ===== EXIT =====
    if message.text == "⬅️ Chiqish":
        user_state[user_id] = "waiting_code"
        await message.answer("Kod kiriting:")
        return

    # ===== CODE =====
    if state == "waiting_code":

        if message.text == ADMIN_CODE:
            user_state[user_id] = "admin"
            await message.answer("Admin panel", reply_markup=admin_main_menu())
            return

        if message.text == CLIENT_CODE:
            user_state[user_id] = "client_name"
            await message.answer("Ismingizni yozing:")
            return

    # ===== CLIENT NAME =====
    if state == "client_name":

        async with pool.acquire() as conn:
            exists = await conn.fetchrow(
                "SELECT id FROM users WHERE telegram_id=$1",
                user_id
            )

            if not exists:
                await conn.execute(
                    "INSERT INTO users(telegram_id,name,role) VALUES($1,$2,'client')",
                    user_id, message.text
                )

        user_state[user_id] = "client"
        await message.answer("Ro‘yxatdan o‘tdingiz", reply_markup=client_menu())
        return

    # ===== CLIENT STAT =====
    if state == "client" and message.text == "Statistika":

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id=$1",
                user_id
            )

        if user:
            remaining = user["total_add"] - user["total_close"]

            await message.answer(
                f"Jami qo‘shilgan: {user['total_add']}\n"
                f"Jami yopilgan: {user['total_close']}\n"
                f"Qolgan: {remaining}"
            )
        return

    # ===== ADMIN LIST =====
    if state == "admin" and message.text == "Mijozlar":

        async with pool.acquire() as conn:
            users = await conn.fetch("SELECT * FROM users WHERE role='client'")

        if not users:
            await message.answer("Mijoz yo‘q")
            return

        text = "Mijozlar:\n\n"
        for u in users:
            remaining = u["total_add"] - u["total_close"]
            text += f"ID:{u['id']} | {u['name']} | Qolgan:{remaining}\n"

        text += "\nMijoz ID sini yozing:"
        user_state[user_id] = "admin_select"
        await message.answer(text)
        return

    # ===== ADMIN SELECT =====
    if state == "admin_select" and message.text.isdigit():

        target_id = int(message.text)

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE id=$1",
                target_id
            )

        if not user:
            await message.answer("Noto‘g‘ri ID")
            return

        admin_context[user_id] = target_id
        user_state[user_id] = "admin_user"

        remaining = user["total_add"] - user["total_close"]

        await message.answer(
            f"{user['name']} statistikasi\n\n"
            f"Qo‘shilgan: {user['total_add']}\n"
            f"Yopilgan: {user['total_close']}\n"
            f"Qolgan: {remaining}",
            reply_markup=admin_user_menu()
        )
        return

    # ===== ADMIN USER MENU =====
    if state == "admin_user":

        if message.text == "⬅️ Orqaga":
            user_state[user_id] = "admin"
            await message.answer("Admin panel", reply_markup=admin_main_menu())
            return

        if message.text == "➕ Qo‘shish":
            user_state[user_id] = "admin_add"
            await message.answer("Nechta dona qo‘shiladi?")
            return

        if message.text == "➖ Yopish":
            user_state[user_id] = "admin_close"
            await message.answer("Nechta dona yopiladi?")
            return

    # ===== ADD =====
    if state == "admin_add" and message.text.isdigit():

        amount = int(message.text)
        target_id = admin_context[user_id]

        await message.answer(
            "Tasdiqlaysizmi?",
            reply_markup=confirm_keyboard("add", target_id, amount)
        )
        return

    # ===== CLOSE =====
    if state == "admin_close" and message.text.isdigit():

        amount = int(message.text)
        target_id = admin_context[user_id]

        await message.answer(
            "Tasdiqlaysizmi?",
            reply_markup=confirm_keyboard("close", target_id, amount)
        )
        return

# ================= CALLBACK =================

@router.callback_query()
async def callback(call: CallbackQuery):

    pool = dp["pool"]
    action, decision, target_id, amount = call.data.split("|")

    target_id = int(target_id)
    amount = int(amount)

    if decision == "yes":

        async with pool.acquire() as conn:

            if action == "add":
                await conn.execute(
                    "UPDATE users SET total_add=total_add+$1 WHERE id=$2",
                    amount, target_id
                )

            if action == "close":
                await conn.execute(
                    "UPDATE users SET total_close=total_close+$1 WHERE id=$2",
                    amount, target_id
                )

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT telegram_id FROM users WHERE id=$1",
                target_id
            )

        if user:
            await bot.send_message(
                user["telegram_id"],
                f"{amount} dona { 'qo‘shildi' if action=='add' else 'yopildi' }."
            )

        await call.message.answer("Bajarildi")

    else:
        await call.message.answer("Rad etildi")

    await call.answer()

# ================= MAIN =================

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
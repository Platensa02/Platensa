import asyncio
import os
import asyncpg

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import CommandStart

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_CODE = "1111"
CLIENT_CODE = "2222"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ================== MEMORY ==================

user_state = {}
temp_action = {}

# ================== DATABASE ==================

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

# ================== KEYBOARDS ==================

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Mijozlar")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Statistika")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def confirm_keyboard(action, user_id, amount):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"{action}|yes|{user_id}|{amount}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"{action}|no|{user_id}|{amount}"
                )
            ]
        ]
    )

# ================== START ==================

@router.message(CommandStart())
async def start(message: Message):
    user_state[message.from_user.id] = "waiting_code"
    await message.answer("Kod kiriting:")

# ================== MAIN HANDLER ==================

@router.message()
async def handler(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id
    pool = dp["pool"]
    state = user_state.get(user_id)

    # BACK
    if message.text == "⬅️ Orqaga":
        user_state[user_id] = "waiting_code"
        await message.answer("Kod kiriting:")
        return

    # ========== CODE STEP ==========

    if state == "waiting_code":

        if message.text == ADMIN_CODE:
            user_state[user_id] = "admin"
            await message.answer("Admin menyu", reply_markup=admin_menu())
            return

        if message.text == CLIENT_CODE:
            user_state[user_id] = "client_name"
            await message.answer("Ismingizni yozing:")
            return

    # ========== CLIENT NAME SAVE ==========

    if state == "client_name":

        async with pool.acquire() as conn:
            exists = await conn.fetchrow(
                "SELECT id FROM users WHERE telegram_id=$1",
                user_id
            )

            if not exists:
                await conn.execute(
                    "INSERT INTO users(telegram_id,name,role) VALUES($1,$2,'client')",
                    user_id,
                    message.text
                )

        user_state[user_id] = "client"
        await message.answer("Ro‘yxatdan o‘tdingiz", reply_markup=client_menu())
        return

    # ========== CLIENT STATISTICS ==========

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

    # ========== ADMIN CLIENT LIST ==========

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
            remaining = u["total_add"] - u["total_close"]
            text += f"ID: {u['id']} | {u['name']} | Qolgan: {remaining}\n"

        text += "\nMijoz ID sini yozing:"
        await message.answer(text)
        return

    # ========== ADMIN SELECT USER ==========

    if state == "admin" and message.text.isdigit():

        temp_action[user_id] = {
            "target": int(message.text)
        }

        await message.answer("Nechta dona?")
        return

    # ========== ADMIN AMOUNT ==========

    if state == "admin" and user_id in temp_action and message.text.isdigit():

        temp_action[user_id]["amount"] = int(message.text)

        await message.answer(
            "Tasdiqlaysizmi?",
            reply_markup=confirm_keyboard(
                "add",
                temp_action[user_id]["target"],
                temp_action[user_id]["amount"]
            )
        )
        return

# ================== CALLBACK ==================

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

        # telegram id olish
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT telegram_id FROM users WHERE id=$1",
                target_id
            )

        if user:
            await bot.send_message(
                user["telegram_id"],
                f"{amount} dona qo‘shildi."
            )

        await call.message.answer("Bajarildi")

    else:
        await call.message.answer("Rad etildi")

    await call.answer()

# ================== MAIN ==================

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
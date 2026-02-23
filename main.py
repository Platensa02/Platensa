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

# ================= STATE =================

user_state = {}
admin_context = {}

# ================= DATABASE INIT =================

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
            [KeyboardButton(text="📋 Mijozlar")],
            [KeyboardButton(text="➕ Qo‘shish")],
            [KeyboardButton(text="➖ Yopish")],
            [KeyboardButton(text="⬅️ Chiqish")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="⬅️ Chiqish")]
        ],
        resize_keyboard=True
    )

# ================= START =================

@router.message(CommandStart())
async def start(message: Message):
    user_state[message.from_user.id] = "waiting_code"
    await message.answer("Kod kiriting:")
# ================= MAIN MESSAGE HANDLER =================

@router.message()


async def main_handler(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id
    text = message.text
    pool = dp["pool"]
    state = user_state.get(user_id)

    # ================= EXIT =================
    if text == "⬅️ Chiqish":
        user_state[user_id] = "waiting_code"
        await message.answer("Kod kiriting:")
        return

    # ================= LOGIN =================
    if state == "waiting_code":

        if text == ADMIN_CODE:
            user_state[user_id] = "admin"
            await message.answer("Admin panelga xush kelibsiz ✅", reply_markup=admin_menu())
            return

        if text == CLIENT_CODE:
            user_state[user_id] = "waiting_name"
            await message.answer("Ismingizni yozing:")
            return

        await message.answer("Noto‘g‘ri kod ❌")
        return

@router.callback_query()
async def callbacks(call: CallbackQuery):
    user_id = call.from_user.id
    pool = dp["pool"]

    if call.data == "cancel":
        user_state[user_id] = "admin"
        await call.message.edit_text("Bekor qilindi.")
        await call.message.answer("Admin panel", reply_markup=admin_menu())
        return

    if call.data == "confirm_add":

        data = admin_context.get(user_id)
        if not data:
            return

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET total_add = total_add + $1 WHERE id=$2",
                data["amount"],
                data["client_id"]
            )

            client = await conn.fetchrow(
                "SELECT telegram_id,total_add,total_close FROM users WHERE id=$1",
                data["client_id"]
            )

        remaining = client["total_add"] - client["total_close"]

        await bot.send_message(
            client["telegram_id"],
            f"📦 {data['amount']} dona qo‘shildi.\n"
            f"📊 Qolgan: {remaining}"
        )

        user_state[user_id] = "admin"
        await call.message.edit_text("Qo‘shildi ✅")
        await call.message.answer("Admin panel", reply_markup=admin_menu())
        return

    if call.data == "confirm_close":

        data = admin_context.get(user_id)
        if not data:
            return

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET total_close = total_close + $1 WHERE id=$2",
                data["amount"],
                data["client_id"]
            )

            client = await conn.fetchrow(
                "SELECT telegram_id,total_add,total_close FROM users WHERE id=$1",
                data["client_id"]
            )

        remaining = client["total_add"] - client["total_close"]

        await bot.send_message(
            client["telegram_id"],
            f"📤 {data['amount']} dona yopildi.\n"
            f"📊 Qolgan: {remaining}"
        )

        user_state[user_id] = "admin"
        await call.message.edit_text("Yopildi ✅")
        await call.message.answer("Admin panel", reply_markup=admin_menu())

    # ================= SAVE CLIENT =================
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

    # ================= CLIENT STAT =================
    if state == "client" and text == "📊 Statistika":

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id=$1",
                user_id
            )

        if user:
            remaining = user["total_add"] - user["total_close"]

            await message.answer(
                f"📦 Qo‘shilgan: {user['total_add']} dona\n"
                f"📤 Yopilgan: {user['total_close']} dona\n"
                f"📊 Qolgan: {remaining} dona"
            )
        return

    # ================= ADMIN VIEW CLIENTS =================
    if state == "admin" and text == "📋 Mijozlar":

        async with pool.acquire() as conn:
            users = await conn.fetch("SELECT * FROM users WHERE role='client'")

        if not users:
            await message.answer("Mijozlar yo‘q.")
            return

        result = "📋 Mijozlar ro‘yxati:\n\n"

        for u in users:
            remaining = u["total_add"] - u["total_close"]
            result += f"ID:{u['id']} | {u['name']} | Qoldiq:{remaining}\n"

        await message.answer(result)
        return
# ================= ADMIN ADD START =================

    if state == "admin" and text == "➕ Qo‘shish":
        user_state[user_id] = "admin_add_id"
        await message.answer("Mijoz ID raqamini kiriting:")
        return

    if state == "admin_add_id":
        admin_context[user_id] = {"client_id": int(text)}
        user_state[user_id] = "admin_add_amount"
        await message.answer("Nechta dona qo‘shiladi?")
        return

    if state == "admin_add_amount":
        admin_context[user_id]["amount"] = int(text)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_add"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")
            ]
        ])

        await message.answer(
            f"{admin_context[user_id]['amount']} dona qo‘shilsinmi?",
            reply_markup=kb
        )
        return


# ================= ADMIN CLOSE START =================

    if state == "admin" and text == "➖ Yopish":
        user_state[user_id] = "admin_close_id"
        await message.answer("Mijoz ID raqamini kiriting:")
        return

    if state == "admin_close_id":
        admin_context[user_id] = {"client_id": int(text)}
        user_state[user_id] = "admin_close_amount"
        await message.answer("Nechta dona yopiladi?")
        return

    if state == "admin_close_amount":
        admin_context[user_id]["amount"] = int(text)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_close"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")
            ]
        ])

        await message.answer(
            f"{admin_context[user_id]['amount']} dona yopilsinmi?",
            reply_markup=kb
        )
        return

import asyncio
import logging
import os
import asyncpg

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command


# =========================
# 🔐 CONFIG (ICHI)
# =========================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8484276514:AAGQImSug67K2JNYJV_h10u1qME1-V_i2l0")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6780565815"))
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://platensa02:ndRSl4NLzhTX1s6OPiOyBZUJcnFEveEL@dpg-d6d2gu1r0fns739jcj4g-a/platensa02")


# =========================
# LOGGING
# =========================

logging.basicConfig(level=logging.INFO)


# =========================
# DATABASE POOL
# =========================

pool = None


async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)


async def create_tables():
    async with pool.acquire() as conn:

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            is_active BOOLEAN DEFAULT TRUE
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS usages(
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount INTEGER,
            confirmed BOOLEAN DEFAULT FALSE
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments(
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount INTEGER
        );
        """)
# =========================
# 📌 STATES
# =========================

class AddClient(StatesGroup):
    waiting_id = State()

class AddUsage(StatesGroup):
    waiting_amount = State()

class AddPayment(StatesGroup):
    waiting_amount = State()


# =========================
# ⌨️ REPLY KEYBOARDS
# =========================

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Mijozlar")],
            [KeyboardButton(text="➕ Mijoz qo‘shish")]
        ],
        resize_keyboard=True
    )


def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Jami ishlatganim")],
            [KeyboardButton(text="📊 Qolganim")]
        ],
        resize_keyboard=True
    )


def back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
        resize_keyboard=True
    )


# =========================
# 🔘 INLINE CONFIRM
# =========================

def confirm_keyboard(usage_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha",
                    callback_data=f"confirm_{usage_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Yo‘q",
                    callback_data=f"reject_{usage_id}"
                )
            ]
        ]
    )


# =========================
# 🚀 START HANDLER
# =========================

async def start_handler(message: Message):

    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👨‍💼 Admin Panel",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            "👤 Mijoz Panel",
            reply_markup=client_menu()
        )
# =========================
# 📥 CREATE USER
# =========================
async def create_user(telegram_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (telegram_id) VALUES ($1) ON CONFLICT DO NOTHING",
            telegram_id
        )


async def get_all_active_users():
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM users WHERE is_active=TRUE ORDER BY id DESC"
        )


async def delete_user(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM users WHERE id=$1",
            user_id
        )


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


# =========================
# 👥 MIJOZLAR TUGMASI
# =========================
async def show_clients(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    clients = await get_all_active_users()

    if not clients:
        await message.answer("❌ Mijozlar yo‘q.")
        return

    keyboard = []

    for client in clients:
        keyboard.append([
            InlineKeyboardButton(
                text=f"👤 {client['telegram_id']}",
                callback_data=f"client_{client['id']}"
            )
        ])

    await message.answer(
        "👥 Mijozlar:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


# =========================
# 👤 MIJOZ KARTASI
# =========================
async def open_client(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(callback.data.split("_")[1])

    used, paid, debt = await get_user_stats(user_id)

    text = (
        f"📊 Hisob:\n\n"
        f"📦 Jami ishlatilgan: {used}\n"
        f"💰 To‘langan: {paid}\n"
        f"📉 Qolgan: {debt}"
    )

    await callback.message.answer(text)

# =========================
# ➕ ADD USAGE START
# =========================
async def start_usage(callback: CallbackQuery, state: FSMContext):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(callback.data.split("_")[2])

    await state.update_data(user_id=user_id)
    await state.set_state(AddUsage.waiting_amount)

    await callback.message.answer("📦 Ishlatish miqdorini kiriting:")


# =========================
# ➕ SAVE USAGE
# =========================
async def save_usage(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting.")
        return

    amount = int(message.text)
    data = await state.get_data()
    user_id = data["user_id"]

    async with pool.acquire() as conn:
        usage_id = await conn.fetchval("""
            INSERT INTO usages (user_id, amount)
            VALUES ($1, $2)
            RETURNING id
        """, user_id, amount)

    await message.bot.send_message(
        user_id,
        f"📦 Siz {amount} dona ishlatdingiz.\nTasdiqlaysizmi?",
        reply_markup=confirm_keyboard(usage_id)
    )

    await message.answer("📨 Mijozga yuborildi.")
    await state.clear()


# =========================
# ✅ CONFIRM USAGE
# =========================
async def confirm_usage(callback: CallbackQuery):

    usage_id = int(callback.data.split("_")[1])

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE usages
            SET confirmed=TRUE
            WHERE id=$1
        """, usage_id)

    await callback.message.answer("✅ Tasdiqlandi.")


# =========================
# ❌ REJECT USAGE
# =========================
async def reject_usage(callback: CallbackQuery):

    usage_id = int(callback.data.split("_")[1])

    async with pool.acquire() as conn:
        await conn.execute("""
            DELETE FROM usages
            WHERE id=$1
        """, usage_id)

    await callback.message.answer("❌ Rad etildi.")


# =========================
# 💰 ADD PAYMENT
# =========================
async def start_payment(callback: CallbackQuery, state: FSMContext):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(callback.data.split("_")[2])

    await state.update_data(user_id=user_id)
    await state.set_state(AddPayment.waiting_amount)

    await callback.message.answer("💰 To‘lov miqdorini kiriting:")


# =========================
# 💰 SAVE PAYMENT + NOTIFY
# =========================
async def save_payment(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting.")
        return

    amount = int(message.text)
    data = await state.get_data()
    user_id = data["user_id"]

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO payments (user_id, amount)
            VALUES ($1, $2)
        """, user_id, amount)

    # Yangi hisob
    used, paid, debt = await get_user_stats(user_id)

    await message.bot.send_message(
        user_id,
        f"💰 Siz {amount} dona to‘ladingiz.\n"
        f"📊 Qolgan: {debt}"
    )

    await message.answer("✅ To‘lov saqlandi.")
    await state.clear()

# =========================
# 📌 REGISTER HANDLERS
# =========================
def register_handlers(dp: Dispatcher):

    # START
    dp.message.register(start_handler, Command("start"))

    # ADMIN BUTTONS
    dp.message.register(show_clients, F.text == "👥 Mijozlar")

    # USAGE CALLBACKS
    dp.callback_query.register(start_usage, F.data.startswith("add_usage_"))
    dp.message.register(save_usage, AddUsage.waiting_amount)
    dp.callback_query.register(confirm_usage, F.data.startswith("confirm_"))
    dp.callback_query.register(reject_usage, F.data.startswith("reject_"))

    # PAYMENT CALLBACKS
    dp.callback_query.register(start_payment, F.data.startswith("add_payment_"))
    dp.message.register(save_payment, AddPayment.waiting_amount)


# =========================
# 🚀 MAIN START
# =========================
async def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await connect_db()
    await create_tables()

    register_handlers(dp)

    print("🚀 CRM PRO SYSTEM v1 ISHGA TUSHDI...")
    await dp.start_polling(bot)


# =========================
# ▶ RUN
# =========================
if __name__ == "__main__":
    asyncio.run(main())
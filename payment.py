import os
import asyncpg

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = None
ADMIN_ID = None
DATABASE_URL = None


# =====================
# SETUP
# =====================
def setup(dp, bot_instance):

    global bot, ADMIN_ID, DATABASE_URL

    bot = bot_instance
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    DATABASE_URL = os.getenv("DATABASE_URL")

    # register handlers
    dp.message(F.text == "💰 To‘lov kiritish")(payment_start)
    dp.callback_query(F.data.startswith("pay_"))(select_payment_client)
    dp.message(Payment.amount)(process_payment)


# =====================
# STATES
# =====================
class Payment(StatesGroup):
    amount = State()


# =====================
# START PAYMENT
# =====================
async def payment_start(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    conn = await asyncpg.connect(DATABASE_URL)
    clients = await conn.fetch("SELECT user_id, name FROM clients")
    await conn.close()

    keyboard = []

    for client in clients:
        keyboard.append([
            InlineKeyboardButton(
                text=client["name"],
                callback_data=f"pay_{client['user_id']}"
            )
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer("To‘lov qaysi mijozga?", reply_markup=markup)


# =====================
# SELECT CLIENT
# =====================
async def select_payment_client(callback: types.CallbackQuery, state: FSMContext):

    user_id = int(callback.data.split("_")[1])

    await state.update_data(user_id=user_id)

    await callback.message.answer("To‘lov summasini yozing:")
    await state.set_state(Payment.amount)

    await callback.answer()


# =====================
# PROCESS PAYMENT
# =====================
async def process_payment(message: types.Message, state: FSMContext):

    data = await state.get_data()
    user_id = data["user_id"]
    amount = int(message.text)

    conn = await asyncpg.connect(DATABASE_URL)

    # To‘lov qo‘shish
    await conn.execute("""
        UPDATE clients
        SET payments = payments + $1
        WHERE user_id=$2
    """, amount, user_id)

    # To‘liq ma’lumot olish
    row = await conn.fetchrow("""
        SELECT confirmed_amount, payments
        FROM clients
        WHERE user_id=$1
    """, user_id)

    await conn.close()

    used = row["confirmed_amount"]
    paid = row["payments"]
    balance = used - paid

    # =====================
    # MIJOZGA TO‘LIQ HISOBOT
    # =====================
    await bot.send_message(
        user_id,
        f"💰 To‘lov qabul qilindi: {amount}\n\n"
        f"📦 Umumiy foydalangan: {used}\n"
        f"💵 To‘langan: {paid}\n"
        f"📊 Qoldiq: {balance}"
    )

    # =====================
    # ADMINGA TO‘LIQ HISOBOT
    # =====================
    await message.answer(
        f"✅ To‘lov saqlandi\n\n"
        f"👤 Mijoz ID: {user_id}\n"
        f"📦 Foydalangan: {used}\n"
        f"💵 To‘langan: {paid}\n"
        f"📊 Qoldiq: {balance}"
    )

    await state.clear()
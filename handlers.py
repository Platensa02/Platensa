import os
import asyncpg

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from menu import admin_menu, client_menu
from report import report_handler

# Global variables
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

    # Start
    dp.message(Command("start"))(start)

    # Admin buttons
    dp.message(F.text == "📦 Mahsulot qo‘shish")(add_product_start)
    dp.message(F.text == "📊 Hisobot")(report_handler)

    # Callback buttons
    dp.callback_query(F.data.startswith("select_"))(select_client)
    dp.callback_query(F.data.startswith("confirm_"))(confirm_product)
    dp.callback_query(F.data == "cancel")(cancel_product)

    # 🔥 FSM handler
    dp.message(AddProduct.amount)(get_amount)


# =====================
# STATES
# =====================
class AddProduct(StatesGroup):
    amount = State()


# =====================
# START
# =====================
async def start(message: types.Message):

    user = message.from_user

    if user.id == ADMIN_ID:
        await message.answer("Admin panel:", reply_markup=admin_menu())
    else:
        await message.answer("Mijoz panel:", reply_markup=client_menu())


# =====================
# ADD PRODUCT
# =====================
async def add_product_start(message: types.Message, state: FSMContext):

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
                callback_data=f"select_{client['user_id']}"
            )
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer("Mijozni tanlang:", reply_markup=markup)


# =====================
# CLIENT SELECT
# =====================
async def select_client(callback: types.CallbackQuery, state: FSMContext):

    user_id = int(callback.data.split("_")[1])

    await state.update_data(user_id=user_id)

    await callback.message.answer("Miqdorni yozing:")
    await state.set_state(AddProduct.amount)

    await callback.answer()


# =====================
# AMOUNT ENTERED
# =====================
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    user_id = data["user_id"]
    amount = int(message.text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"confirm_{user_id}_{amount}"
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="cancel"
            )
        ]
    ])

    await bot.send_message(
        user_id,
        f"📦 Sizga {amount} dona qo‘shildi.\nTasdiqlaysizmi?",
        reply_markup=keyboard
    )

    await message.answer("Mijozga yuborildi ✅")
    await state.clear()


# =====================
# CONFIRM
# =====================
async def confirm_product(callback: types.CallbackQuery):

    _, user_id, amount = callback.data.split("_")

    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        UPDATE clients
        SET confirmed_amount = confirmed_amount + $1
        WHERE user_id=$2
    """, int(amount), int(user_id))

    await conn.close()

    # 🔥 MIJOZGA XABAR
    await bot.send_message(
        int(user_id),
        f"✅ Tasdiqlandi!\n📦 Qo‘shildi: {amount} dona"
    )

    # 🔥 ADMINGA XABAR
    await bot.send_message(
        ADMIN_ID,
        f"📢 Mijoz tasdiqladi!\👤 Ism: {client_name}\n📦 Miqdor: {amount}"
    )

    await callback.message.edit_text("✅ Tasdiqlandi!")
    await callback.answer()

# =====================
# CANCEL
# =====================
async def cancel_product(callback: types.CallbackQuery):

    # 🔥 ADMINGA XABAR
    await bot.send_message(
        ADMIN_ID,
        "❌ Mijoz mahsulotni rad etdi."
    )

    await callback.message.edit_text("❌ Bekor qilindi")
    await callback.answer() 
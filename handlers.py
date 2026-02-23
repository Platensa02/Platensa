import os
import asyncpg

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from menu import admin_menu, client_menu
from report import report_handler

bot = None
ADMIN_ID = None
DATABASE_URL = None


# =====================
# STATES
# =====================
class AddProduct(StatesGroup):
    amount = State()


# =====================
# SETUP
# =====================
def setup(dp, bot_instance):

    global bot, ADMIN_ID, DATABASE_URL

    bot = bot_instance
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Commands
    dp.message(Command("start"))(start)

    # Buttons
    dp.message(F.text == "📦 Mahsulot qo‘shish")(add_product_start)
    dp.message(F.text == "📊 Hisobot")(report_handler)

    # Callbacks
    dp.callback_query(F.data.startswith("select_"))(select_client)

    dp.callback_query(
        F.data.startswith("confirm_") &
        ~F.data.startswith("confirm_delete_")
    )(confirm_product)

    dp.callback_query(F.data == "cancel")(cancel_product)

    # 🔥 YANGI TASDIQLASH CALLBACKLARI
    dp.callback_query(F.data.startswith("approve_"))(approve_client)
    dp.callback_query(F.data.startswith("reject_"))(reject_client)

    # FSM
    dp.message(AddProduct.amount)(get_amount)

# =====================
# START
# =====================
 
async def start(message: types.Message):

    user = message.from_user

    if user.id == ADMIN_ID:
        await message.answer("Admin panel:", reply_markup=admin_menu())
        return

    conn = await asyncpg.connect(DATABASE_URL)

    existing = await conn.fetchrow(
        "SELECT * FROM clients WHERE user_id=$1",
        user.id
    )

    # Agar yangi mijoz bo‘lsa
    if not existing:

        await conn.execute("""
            INSERT INTO clients (user_id, name, confirmed_amount, payments)
            VALUES ($1, $2, 0, 0)
        """, user.id, user.full_name)

        # 🔥 ADMINGA XABAR
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi mijoz kirdi:\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}"
        )

    await conn.close()

    await message.answer("Mijoz panel:", reply_markup=client_menu())
   
# =====================
# ADD PRODUCT START
# =====================
async def add_product_start(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    conn = await asyncpg.connect(DATABASE_URL)
    clients = await conn.fetch("SELECT user_id, name FROM clients")
    await conn.close()

    keyboard = [
        [InlineKeyboardButton(
            text=c["name"],
            callback_data=f"select_{c['user_id']}"
        )]
        for c in clients
    ]

    await message.answer(
        "Mijozni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


# =====================
# SELECT CLIENT
# =====================
async def select_client(callback: types.CallbackQuery, state: FSMContext):

    user_id = int(callback.data.split("_")[1])

    await state.update_data(user_id=user_id)

    await callback.message.answer("Miqdorni yozing:")
    await state.set_state(AddProduct.amount)

    await callback.answer()


# =====================
# GET AMOUNT
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

    if not callback.data.startswith("confirm_"):
        return

    _, user_id, amount = callback.data.split("_")
    user_id = int(user_id)
    amount = int(amount)

    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        UPDATE clients
        SET confirmed_amount = confirmed_amount + $1
        WHERE user_id=$2
    """, amount, user_id)

    client = await conn.fetchrow(
        "SELECT name FROM clients WHERE user_id=$1",
        user_id
    )

    await conn.close()

    name = client["name"] if client else "Noma’lum"

    await bot.send_message(
        user_id,
        f"✅ Tasdiqlandi!\n📦 Qo‘shildi: {amount} dona"
    )

    await bot.send_message(
        ADMIN_ID,
        f"📢 Tasdiqlandi\n👤 Ism: {name}\n📦 Miqdor: {amount}"
    )

    await callback.message.edit_text("✅ Tasdiqlandi!")
    await callback.answer()
async def approve_client(callback: types.CallbackQuery):

    user_id = int(callback.data.split("_")[1])

    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        UPDATE clients
        SET is_approved=TRUE
        WHERE user_id=$1
    """, user_id)

    await conn.close()

    await bot.send_message(user_id, "✅ Siz tasdiqlandingiz!")

    await callback.message.edit_text("✅ Mijoz tasdiqlandi.")
    await callback.answer()

# =====================
# APPROVE NEW CLIENT
# =====================
async def approve_client(callback: types.CallbackQuery):

    if not callback.data.startswith("approve_"):
        return

    try:
        user_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("Xatolik ❌", show_alert=True)
        return

    conn = await asyncpg.connect(DATABASE_URL)

    # is_approved ni TRUE qilamiz
    await conn.execute("""
        UPDATE clients
        SET is_approved = TRUE
        WHERE user_id = $1
    """, user_id)

    client = await conn.fetchrow(
        "SELECT name FROM clients WHERE user_id=$1",
        user_id
    )

    await conn.close()

    name = client["name"] if client else "Noma’lum"

    # MIJOZGA XABAR
    await bot.send_message(
        user_id,
        "✅ Siz admin tomonidan tasdiqlandingiz!"
    )

    # ADMINGA XABAR
    await callback.message.edit_text(
        f"✅ Mijoz tasdiqlandi\n👤 {name}"
    )

    await callback.answer()


# =====================
# REJECT NEW CLIENT
# =====================
async def reject_client(callback: types.CallbackQuery):

    if not callback.data.startswith("reject_"):
        return

    try:
        user_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("Xatolik ❌", show_alert=True)
        return

    conn = await asyncpg.connect(DATABASE_URL)

    # Mijozni butunlay o‘chiramiz
    await conn.execute(
        "DELETE FROM clients WHERE user_id=$1",
        user_id
    )

    await conn.close()

    # MIJOZGA XABAR
    await bot.send_message(
        user_id,
        "❌ Sizning so‘rovingiz rad etildi."
    )

    await callback.message.edit_text("❌ Mijoz rad etildi.")
    await callback.answer()

# =====================
# CANCEL CALLBACK
# =====================
async def cancel_product(callback: types.CallbackQuery):

    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()

import os
import asyncpg

from aiogram import types, F
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

    dp.message(F.text == "🗑 Mijoz o‘chirish")(delete_start)
    dp.callback_query(F.data.startswith("delete_"))(ask_confirm)
    dp.callback_query(F.data.startswith("confirm_delete_"))(confirm_delete)
    dp.callback_query(F.data == "cancel_delete")(cancel_delete)


# =====================
# DELETE START
# =====================
async def delete_start(message: types.Message):

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
                callback_data=f"delete_{client['user_id']}"
            )
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer("Qaysi mijozni o‘chirasiz?", reply_markup=markup)


# =====================
# ASK CONFIRMATION
# =====================
async def ask_confirm(callback: types.CallbackQuery):

    user_id = callback.data.split("_")[1]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Ha",
                callback_data=f"confirm_delete_{user_id}"
            ),
            InlineKeyboardButton(
                text="❌ Yo‘q",
                callback_data="cancel_delete"
            )
        ]
    ])

    await callback.message.edit_text(
        "⚠️ Mijozni to‘liq o‘chirasizmi?",
        reply_markup=keyboard
    )

    await callback.answer()


# =====================
# CONFIRM DELETE
# =====================
async def confirm_delete(callback: types.CallbackQuery):

    user_id = int(callback.data.split("_")[2])

    conn = await asyncpg.connect(DATABASE_URL)

    # Mijozni o‘chirish
    await conn.execute(
        "DELETE FROM clients WHERE user_id=$1",
        user_id
    )

    # Agar alohida jadval bo‘lsa tozalash
    await conn.execute(
        "DELETE FROM payments WHERE user_id=$1",
        user_id
    )

    await conn.execute(
        "DELETE FROM products WHERE user_id=$1",
        user_id
    )

    await conn.close()

    await bot.send_message(
        user_id,
        "❌ Siz admin tomonidan tizimdan o‘chirildingiz."
    )

    await callback.message.edit_text("✅ Mijoz to‘liq o‘chirildi.")
    await callback.answer()


# =====================
# CANCEL
# =====================
async def cancel_delete(callback: types.CallbackQuery):

    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()
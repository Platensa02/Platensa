
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

    # 🔒 aniq prefixlar
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

    if not clients:
        await message.answer("Mijozlar yo‘q.")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                text=client["name"],
                callback_data=f"delete_{client['user_id']}"
            )
        ]
        for client in clients
    ]

    await message.answer(
        "Qaysi mijozni o‘chirasiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


# =====================
# ASK CONFIRM
# =====================
async def ask_confirm(callback: types.CallbackQuery):

    # 🔒 noto‘g‘ri callback tushmasligi uchun
    if not callback.data.startswith("delete_"):
        return

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
        "⚠️ Mijozni to‘liq o‘chirasizmi?\n(Barcha mahsulot va to‘lovlar ham o‘chadi)",
        reply_markup=keyboard
    )

    await callback.answer()


# =====================
# CONFIRM DELETE
# =====================
async def confirm_delete(callback: types.CallbackQuery):

    if not callback.data.startswith("confirm_delete_"):
        return

    try:
        user_id = int(callback.data.split("_")[2])
    except:
        await callback.answer("Xatolik ❌", show_alert=True)
        return

    conn = await asyncpg.connect(DATABASE_URL)

    # Mijoz nomini olish
    client = await conn.fetchrow(
        "SELECT name FROM clients WHERE user_id=$1",
        user_id
    )

    client_name = client["name"] if client else "Noma’lum"

    # 🔥 MIJOZGA XABAR
    try:
        await bot.send_message(
            user_id,
            "❌ Siz admin tomonidan tizimdan o‘chirildingiz."
        )
    except:
        pass

    # 🔥 BAZADAN O‘CHIRISH
    await conn.execute("DELETE FROM clients WHERE user_id=$1", user_id)

    await conn.close()

    # 🔥 ADMINGA CHIROYLI XABAR
    await callback.message.edit_text(
        f"✅ Mijoz o‘chirildi.\n👤 Ism: {client_name}"
    )

    await callback.answer()


# =====================
# CANCEL
# =====================
async def cancel_delete(callback: types.CallbackQuery):

    await callback.message.edit_text("❌ O‘chirish bekor qilindi.")
    await callback.answer()
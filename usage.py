import os
import asyncpg
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

def setup_usage_handlers(dp, bot):
    dp.message(F.text == "📉 Ishlatilgan")(lambda msg: used_start(msg, bot))
    dp.callback_query(F.data.startswith("use_"))(lambda cb: show_used(cb, bot))

async def used_start(message: types.Message, bot):
    if message.from_user.id != ADMIN_ID:
        return
    conn = await asyncpg.connect(DATABASE_URL)
    clients = await conn.fetch("SELECT user_id, name FROM clients")
    await conn.close()

    keyboard = [[InlineKeyboardButton(text=c["name"], callback_data=f"use_{c['user_id']}")] for c in clients]
    await message.answer("Mijozni tanlang (ishlatilgan mahsulotni ko‘rish uchun):", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

async def show_used(callback, bot):
    user_id = int(callback.data.split("_")[1])
    conn = await asyncpg.connect(DATABASE_URL)
    client = await conn.fetchrow("SELECT name, confirmed_amount, used_amount FROM clients WHERE user_id=$1", user_id)
    await conn.close()
    if not client:
        await callback.answer("❌ Mijoz topilmadi!", show_alert=True)
        return
    confirmed = client["confirmed_amount"]
    used = client.get("used_amount", 0)
    remaining = confirmed - used
    await callback.message.edit_text(f"👤 {client['name']}\n📦 Umumiy qo‘shilgan: {confirmed}\n🔹 Ishlatilgan: {used}\n📊 Qoldiq: {remaining}")
    await callback.answer()
import asyncpg
from aiogram import F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DATABASE_URL = None
bot = None
ADMIN_ID = None

def setup_usage_handlers(dp, bot_instance):
    global bot, DATABASE_URL, ADMIN_ID
    bot = bot_instance
    import os
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))

    dp.message(F.text == "📉 Ishlatilgan")(used_start)


async def used_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    conn = await asyncpg.connect(DATABASE_URL)
    clients = await conn.fetch("SELECT user_id, name FROM clients")
    await conn.close()

    keyboard = [
        [InlineKeyboardButton(text=c["name"], callback_data=f"use_{c['user_id']}")]
        for c in clients
    ]

    await message.answer(
        "Mijozni tanlang (ishlatilgan mahsulotni ko‘rish uchun):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
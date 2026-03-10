import os
from aiogram import types, F
from aiogram.filters import Command
from menu import admin_menu, client_menu
from report import report_handler
from add_product import setup_add_product_handlers
from usage import setup_usage_handlers

bot = None
ADMIN_ID = None
DATABASE_URL = None

def setup(dp, bot_instance):
    global bot, ADMIN_ID, DATABASE_URL
    bot = bot_instance
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    DATABASE_URL = os.getenv("DATABASE_URL")

    # /start komandasi
    dp.message(Command("start"))(start)

    # Bosh menyu tugmalari
    dp.message(F.text == "📊 Hisobot")(report_handler)

    # Qo‘shilgan modul handlerlarini chaqiramiz
    setup_add_product_handlers(dp, bot)
    setup_usage_handlers(dp, bot)


async def start(message: types.Message):
    user = message.from_user

    if user.id == ADMIN_ID:
        await message.answer("Admin panel:", reply_markup=admin_menu())
        return

    import asyncpg
    conn = await asyncpg.connect(DATABASE_URL)

    existing = await conn.fetchrow(
        "SELECT * FROM clients WHERE user_id=$1",
        user.id
    )

    if not existing:
        await conn.execute("""
            INSERT INTO clients (user_id, name, confirmed_amount, payments)
            VALUES ($1, $2, 0, 0)
        """, user.id, user.full_name)

        # ADMINGA XABAR
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi mijoz kirdi:\n👤 {user.full_name}\n🆔 ID: {user.id}"
        )

    await conn.close()
    await message.answer("Mijoz panel:", reply_markup=client_menu())
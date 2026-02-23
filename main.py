from aiogram import types
from aiogram.filters import Command
import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user

    conn = await asyncpg.connect(DATABASE_URL)

    # user bazada bormi tekshiramiz
    client = await conn.fetchrow(
        "SELECT * FROM clients WHERE user_id=$1",
        user.id
    )

    # Agar yo'q bo'lsa qo'shamiz
    if not client:
        await conn.execute(
            "INSERT INTO clients (user_id, name) VALUES ($1, $2)",
            user.id,
            user.full_name
        )

        # Admin ga xabar
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi mijoz qo‘shildi:\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}"
        )

    await conn.close()

    await message.answer("Botga xush kelibsiz ✅")
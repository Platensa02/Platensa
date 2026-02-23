import os
import asyncio
import asyncpg

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from menu import admin_menu

# =====================
# ENV VARIABLES
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

# =====================
# BOT & DP
# =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# =====================
# START COMMAND
# =====================
@dp.message(Command("start"))
async def start(message: types.Message):

    user = message.from_user

    # ===== ADMIN =====
    if user.id == ADMIN_ID:
        await message.answer("Admin panel:", reply_markup=admin_menu())
        return

    # ===== CLIENT =====
    conn = await asyncpg.connect(DATABASE_URL)

    client = await conn.fetchrow(
        "SELECT * FROM clients WHERE user_id=$1",
        user.id
    )

    if not client:
        await conn.execute(
            "INSERT INTO clients (user_id, name) VALUES ($1, $2)",
            user.id,
            user.full_name
        )

        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi mijoz qo‘shildi:\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}"
        )

    await conn.close()

    await message.answer("Bot ishlayapti ✅")

# =====================
# MAIN
# =====================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
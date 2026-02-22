import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID
from database import connect_db, create_tables, close_db

from handlers import start, admin, usage, payment
from keyboards.reply import admin_menu, client_menu


# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)


# =========================
# MAIN
# =========================
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # 🔥 DATABASE
    await connect_db()
    await create_tables()

    # 🔥 ROUTERS
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(usage.router)
    dp.include_router(payment.router)

    # 🔥 START COMMAND
    @dp.message(Command("start"))
    async def start_handler(message: Message):
        if message.from_user.id == ADMIN_ID:
            await message.answer(
                "👨‍💼 Admin Panel",
                reply_markup=admin_menu()
            )
        else:
            await message.answer(
                "👤 Mijoz Panel",
                reply_markup=client_menu()
            )

    # 🔥 BOT START
    logging.info("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)

    # 🔥 CLEAN EXIT
    await close_db()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    asyncio.run(main())
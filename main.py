import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN
from database import connect_db, create_tables, close_db

# Handlers
from handlers import start
from handlers import admin
from handlers import usage
from handlers import payment


# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)


# =========================
# MAIN FUNCTION
# =========================
async def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Database ulash
    await connect_db()
    await create_tables()

    # Routers qo‘shish
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(usage.router)
    dp.include_router(payment.router)

    # Bot ishga tushdi
    logging.info("🚀 CRM PRO SYSTEM v1 ishga tushdi...")

    await dp.start_polling(bot)

    # Yopish (agar kerak bo‘lsa)
    await close_db()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    asyncio.run(main())
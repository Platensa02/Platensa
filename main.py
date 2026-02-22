import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from database import create_pool, init_db

from handlers import admin, client, admin_clients, usage, payment
from keyboards import admin_menu, client_menu


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Database
    pool = await create_pool()
    dp["db"] = pool
    await init_db(pool)

    # Routers
    dp.include_router(admin.router)
    dp.include_router(client.router)
    dp.include_router(admin_clients.router)
    dp.include_router(usage.router)
    dp.include_router(payment.router)

    # START
    @dp.message(Command("start"))
    async def start(message: Message):
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

    print("🚀 CRM Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

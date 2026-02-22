import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from database import create_pool, init_db
from handlers import admin, client
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

    # START COMMAND
    @dp.message(Command("start"))
    async def start_handler(message: Message):
        user_id = message.from_user.id

        if user_id == ADMIN_ID:
            await message.answer(
                "👨‍💼 Admin panel",
                reply_markup=admin_menu()
            )
        else:
            # User aktivligini tekshirish
            async with pool.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT is_active FROM users WHERE telegram_id=$1",
                    user_id
                )

            if not user or not user["is_active"]:
                await message.answer("⛔ Sizga ruxsat berilmagan.")
                return

            await message.answer(
                "👤 Mijoz panel",
                reply_markup=client_menu()
            )

    print("🚀 CRM Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

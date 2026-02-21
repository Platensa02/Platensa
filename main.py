import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID
from database import create_pool, init_db
from handlers import admin, client
from keyboards import admin_menu, client_panel


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Database ulash
    pool = await create_pool()
    dp["db"] = pool

    # Jadval yaratish
    await init_db(pool)

    # Routerlarni ulash
    dp.include_router(admin.router)
    dp.include_router(client.router)

    # START handler
    @dp.message(Command("start"))
    async def start_handler(message: Message):
        if message.from_user.id == ADMIN_ID:
            await message.answer(
                "👨‍💼 Admin panel",
                reply_markup=admin_menu()
            )
        else:
            await message.answer(
                "👤 Mijoz panel",
                reply_markup=client_panel()
            )

    print("🚀 Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

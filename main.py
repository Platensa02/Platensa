import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import create_pool, init_db

# Routerlar
from handlers import admin, client

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

    print("🚀 Bot ishga tushdi...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

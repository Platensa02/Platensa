import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, DATABASE_URL
from database import init_db

from handlers import start, admin, client

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await init_db(dp, DATABASE_URL)

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(client.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
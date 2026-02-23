import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, DATABASE_URL
from database import init_db
import handlers

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await init_db(dp, DATABASE_URL)

    dp.include_router(handlers.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
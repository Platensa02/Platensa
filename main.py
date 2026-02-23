import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, DATABASE_URL
import database
from handlers import router

async def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await database.init_db(DATABASE_URL)

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
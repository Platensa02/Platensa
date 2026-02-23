import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncpg
from database import init_db

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DATABASE_URL = os.getenv("DATABASE_URL")


async def get_conn():
    return await asyncpg.connect(DATABASE_URL)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Bot ishlayapti ✅")


async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db
import handlers

# =====================
# ENV VARIABLES
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =====================
# BOT & DP
# =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# =====================
# HANDLERS ULASH
# =====================
handlers.setup(dp, bot)

# =====================
# MAIN
# =====================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
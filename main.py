# =======================
# MAIN.PY
# Bu fayl faqat botni ishga tushiradi
# =======================

import os
print("DATABASE_URL =", os.getenv("DATABASE_URL"))
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db
import handlers
import payment
import delete

# =====================
# ENV VARIABLES
# =====================
# Railway Variables ichida bo‘lishi kerak:
# BOT_TOKEN
# ADMIN_ID
# DATABASE_URL

BOT_TOKEN = os.getenv("BOT_TOKEN")

# =====================
# BOT & DP YARATISH
# =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# =====================
# HANDLERS ULASH
# =====================
# Bu juda muhim!
# handlers.py ichidagi funksiyalar shu yerda ulanadi
handlers.setup(dp, bot)
payment.setup(dp, bot)
delete.setup(dp, bot)

# =====================
# MAIN FUNKSIYA
# =====================
async def main():
    await init_db()      # database yaratish
    await dp.start_polling(bot)   # botni ishga tushirish

if __name__ == "__main__":
    asyncio.run(main())
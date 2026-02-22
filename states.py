from aiogram.fsm.state import State, StatesGroup


# ➕ Ishlatish qo‘shish
class AddUsage(StatesGroup):
    waiting_amount = State()


# 💰 To‘lov qo‘shish
class AddPayment(StatesGroup):
    waiting_amount = State()


# 👤 Yangi mijoz qo‘shish (agar kerak bo‘lsa)
class AddClient(StatesGroup):
    waiting_telegram_id = State()
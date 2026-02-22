from aiogram.fsm.state import State, StatesGroup

# ➕ Mijoz qo‘shish
class AddClient(StatesGroup):
    waiting_for_id = State()

# ➕ Ishlatish miqdori
class AddUsage(StatesGroup):
    waiting_for_amount = State()

# 💰 To‘lov miqdori
class AddPayment(StatesGroup):
    waiting_for_amount = State()

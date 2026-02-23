import os
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from menu import admin_menu, client_menu

ADMIN_ID = int(os.getenv("ADMIN_ID"))
ACCESS_CODE = os.getenv("ACCESS_CODE")

# =====================
# STATES
# =====================
class Access(StatesGroup):
    code = State()


# =====================
# SETUP
# =====================
def setup(dp):

    dp.message(Command("start"))(start)
    dp.message(Access.code)(check_code)


# =====================
# START
# =====================
async def start(message: types.Message, state: FSMContext):

    user = message.from_user

    # Admin darrov kiradi
    if user.id == ADMIN_ID:
        await message.answer("Admin panel:", reply_markup=admin_menu())
        return

    # Kod so‘raymiz
    await message.answer("🔐 Kirish kodini kiriting:")
    await state.set_state(Access.code)


# =====================
# KOD TEKSHIRISH
# =====================
async def check_code(message: types.Message, state: FSMContext):

    if message.text == ACCESS_CODE:
        await message.answer("✅ Kirish tasdiqlandi!", reply_markup=client_menu())
        await state.clear()
    else:
        await message.answer("❌ Kod noto‘g‘ri. Qayta urinib ko‘ring.")
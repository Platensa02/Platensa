from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

# Mijozlar tugmasi (hozircha oddiy)
@router.callback_query(F.data == "clients")
async def clients_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("👥 Mijozlar bo‘limi (keyingi bosqichda to‘liq qilamiz)")

# Orqaga
@router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🔙 Orqaga")

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from config import ADMIN_ID
from keyboards import admin_menu

router = Router()

# Admin tekshiruvi
def is_admin(user_id):
    return user_id == ADMIN_ID

# Admin start (faqat admin uchun)
@router.message()
async def admin_start(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer("👨‍💼 Admin panel", reply_markup=admin_menu())

# Back tugma
@router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    await callback.answer()  # 🔥 MUHIM

    if not is_admin(callback.from_user.id):
        return

    await callback.message.answer("🔙 Bosh menyu", reply_markup=admin_menu())

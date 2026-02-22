from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID
from database import get_user_by_tg, create_user
from keyboards.reply import admin_menu, client_menu

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):

    user_id = message.from_user.id

    # ADMIN
    if user_id == ADMIN_ID:
        await message.answer("👨‍💼 Admin Panel", reply_markup=admin_menu())
        return

    # CLIENT
    user = await get_user_by_tg(user_id)

    # Agar user yo‘q bo‘lsa — yaratamiz
    if not user:
        await create_user(user_id)
        user = await get_user_by_tg(user_id)

    # Agar blok bo‘lsa
    if not user["is_active"]:
        await message.answer("⛔ Sizga ruxsat yo‘q.")
        return

    await message.answer("👤 Mijoz Panel", reply_markup=client_menu())
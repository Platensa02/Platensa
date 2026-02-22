from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import ADMIN_ID
from database import get_all_active_users, delete_user, get_user_stats
from keyboards.inline import (
    clients_list_keyboard,
    client_actions_keyboard
)
from keyboards.reply import admin_menu

router = Router()


# =========================
# 👥 MIJOZLAR RO‘YXATI
# =========================
@router.message(F.text == "👥 Mijozlar")
async def show_clients(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    clients = await get_all_active_users()

    if not clients:
        await message.answer("❌ Mijozlar yo‘q.")
        return

    await message.answer(
        "👥 Mijozlar ro‘yxati:",
        reply_markup=clients_list_keyboard(clients)
    )


# =========================
# 👤 MIJOZ TANLASH
# =========================
@router.callback_query(F.data.startswith("client_"))
async def open_client(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(callback.data.split("_")[1])

    used, paid, debt = await get_user_stats(user_id)

    text = (
        f"👤 Mijoz ID: {user_id}\n\n"
        f"📦 Jami ishlatilgan: {used}\n"
        f"💰 To‘langan: {paid}\n"
        f"📊 Qolgan: {debt}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=client_actions_keyboard(user_id)
    )


# =========================
# 🗑 FULL DELETE
# =========================
@router.callback_query(F.data.startswith("delete_user_"))
async def delete_client(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(callback.data.split("_")[1])

    await delete_user(user_id)

    await callback.message.answer("🗑 Mijoz to‘liq o‘chirildi.")


# =========================
# 🔙 ORQAGA
# =========================
@router.callback_query(F.data == "back")
async def back_to_admin(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.answer(
        "👨‍💼 Admin Panel",
        reply_markup=admin_menu()
    )
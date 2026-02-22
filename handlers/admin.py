from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import AddClient
from config import ADMIN_ID

router = Router()

# ➕ Mijoz qo‘shish tugmasi
@router.callback_query(F.data == "clients")
async def clients_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.from_user.id != ADMIN_ID:
        return

    # State yoqamiz
    await state.set_state(AddClient.waiting_for_id)

    await callback.message.answer("👥 Mijoz Telegram ID sini yozing:")


# 📩 ID qabul qilish
@router.message(AddClient.waiting_for_id)
async def process_client_id(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    # Raqam tekshirish
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    user_id = int(message.text)

    pool = message.bot.get("db")

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id, is_active)
            VALUES ($1, TRUE)
            ON CONFLICT (telegram_id)
            DO UPDATE SET is_active = TRUE
        """, user_id)

    await message.answer("✅ Mijoz muvaffaqiyatli qo‘shildi.")

    # State tozalash
    await state.clear()

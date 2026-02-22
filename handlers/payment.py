from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from states import AddPayment
from database import pool, get_user_stats

router = Router()


# =========================
# 💰 TO‘LOV BOSHLASH
# =========================
@router.callback_query(F.data.startswith("add_payment_"))
async def start_payment(callback: CallbackQuery, state: FSMContext):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(callback.data.split("_")[2])

    await state.update_data(user_id=user_id)

    await callback.message.answer("💰 To‘lov miqdorini kiriting:")
    await state.set_state(AddPayment.waiting_amount)


# =========================
# 📩 MIQDOR QABUL QILISH
# =========================
@router.message(AddPayment.waiting_amount)
async def save_payment(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting.")
        return

    amount = int(message.text)
    data = await state.get_data()
    user_id = data["user_id"]

    # To‘lovni saqlash
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO payments (user_id, amount)
            VALUES ($1, $2)
        """, user_id, amount)

    # Yangi hisobni olish
    used, paid, debt = await get_user_stats(user_id)

    # Mijozga xabar
    await message.bot.send_message(
        user_id,
        f"💰 Siz {amount} dona to‘ladingiz.\n"
        f"📊 Qolgan: {debt}"
    )

    await message.answer("✅ To‘lov saqlandi va mijozga yuborildi.")
    await state.clear()
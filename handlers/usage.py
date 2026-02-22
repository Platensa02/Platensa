from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from states import AddUsage
from database import pool, confirm_usage, reject_usage
from keyboards.inline import confirm_usage_keyboard

router = Router()


# =========================
# ➕ ISHLATISH BOSHLASH
# =========================
@router.callback_query(F.data.startswith("add_usage_"))
async def start_usage(callback: CallbackQuery, state: FSMContext):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(callback.data.split("_")[2])

    await state.update_data(user_id=user_id)

    await callback.message.answer("📦 Ishlatish miqdorini kiriting:")
    await state.set_state(AddUsage.waiting_amount)


# =========================
# 📩 MIQDOR QABUL QILISH
# =========================
@router.message(AddUsage.waiting_amount)
async def save_usage(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting.")
        return

    amount = int(message.text)
    data = await state.get_data()
    user_id = data["user_id"]

    async with pool.acquire() as conn:
        usage_id = await conn.fetchval("""
            INSERT INTO usages (user_id, amount)
            VALUES ($1, $2)
            RETURNING id
        """, user_id, amount)

    # Mijozga tasdiqlash xabari
    await message.bot.send_message(
        user_id,
        f"📦 Siz {amount} dona ishlatdingiz.\nTasdiqlaysizmi?",
        reply_markup=confirm_usage_keyboard(usage_id)
    )

    await message.answer("📨 Mijozga yuborildi.")
    await state.clear()


# =========================
# ✅ TASDIQLASH
# =========================
@router.callback_query(F.data.startswith("confirm_"))
async def confirm_usage_handler(callback: CallbackQuery):

    usage_id = int(callback.data.split("_")[1])

    await confirm_usage(usage_id)

    await callback.message.answer("✅ Tasdiqlandi.")


# =========================
# ❌ RAD ETISH
# =========================
@router.callback_query(F.data.startswith("reject_"))
async def reject_usage_handler(callback: CallbackQuery):

    usage_id = int(callback.data.split("_")[1])

    await reject_usage(usage_id)

    await callback.message.answer("❌ Rad etildi.")
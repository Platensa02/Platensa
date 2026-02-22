from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from keyboards import admin_menu, confirm_keyboard
from states import AddClient, AddUsage, AddPayment

router = Router()

# 🔐 ADMIN CHECK
def is_admin(user_id):
    return user_id == ADMIN_ID


# 👥 Mijozlar menyusi
@router.callback_query(F.data == "clients")
async def clients_menu(callback: CallbackQuery):
    await callback.answer()

    if not is_admin(callback.from_user.id):
        return

    await callback.message.answer(
        "➕ Mijoz Telegram ID yuboring:",
    )


# =========================
# ➕ MIJOZ QO‘SHISH
# =========================

@router.message(AddClient.waiting_for_id)
async def add_client(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    pool = message.bot.get("db")

    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (telegram_id, is_active)
        VALUES ($1, TRUE)
        ON CONFLICT (telegram_id)
        DO UPDATE SET is_active=TRUE
        """, int(message.text))

    await message.answer("✅ Mijoz qo‘shildi")
    await state.clear()


# =========================
# ➕ ISHLATISH
# =========================

@router.callback_query(F.data.startswith("use_"))
async def add_usage(callback: CallbackQuery):
    await callback.answer()

    if not is_admin(callback.from_user.id):
        return

    user_id = int(callback.data.split("_")[1])

    pool = callback.bot.get("db")

    # misol uchun 10 dona qo‘shamiz (keyin FSM qilamiz)
    amount = 10

    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
        INSERT INTO usage (user_id, amount)
        VALUES ($1, $2)
        RETURNING id
        """, user_id, amount)

    usage_id = result["id"]

    await callback.bot.send_message(
        user_id,
        f"📦 Siz {amount} dona ishlatdingiz.\nTasdiqlaysizmi?",
        reply_markup=confirm_keyboard(usage_id)
    )


# =========================
# ✅ TASDIQLASH
# =========================

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_usage(callback: CallbackQuery):
    await callback.answer()

    usage_id = int(callback.data.split("_")[1])

    pool = callback.bot.get("db")

    async with pool.acquire() as conn:
        await conn.execute("""
        UPDATE usage
        SET confirmed=TRUE
        WHERE id=$1
        """, usage_id)

    await callback.message.answer("✅ Tasdiqlandi")

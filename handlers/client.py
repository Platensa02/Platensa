from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import client_panel
from config import ADMIN_ID

router = Router()

# Mijoz panelini ko'rsatish
@router.callback_query(F.data == "client_menu")
async def client_menu_handler(callback: CallbackQuery):
    await callback.message.answer(
        "📊 Mijoz panel",
        reply_markup=client_panel()
    )

# Jami ishlatgan
@router.callback_query(F.data == "my_used")
async def my_used(callback: CallbackQuery):
    pool = callback.bot.get("db")

    async with pool.acquire() as conn:
        total = await conn.fetchval("""
            SELECT COALESCE(SUM(amount),0)
            FROM usage
            WHERE user_id=$1 AND confirmed=TRUE
        """, callback.from_user.id)

    await callback.message.answer(f"📦 Jami ishlatganingiz: {total} dona")

# Qolgan dona
@router.callback_query(F.data == "my_left")
async def my_left(callback: CallbackQuery):
    pool = callback.bot.get("db")

    async with pool.acquire() as conn:
        used = await conn.fetchval("""
            SELECT COALESCE(SUM(amount),0)
            FROM usage
            WHERE user_id=$1 AND confirmed=TRUE
        """, callback.from_user.id)

        paid = await conn.fetchval("""
            SELECT COALESCE(SUM(amount),0)
            FROM payments
            WHERE user_id=$1
        """, callback.from_user.id)

    left = used - paid
    await callback.message.answer(f"📊 To'lanmagan dona: {left}")

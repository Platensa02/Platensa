from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# 👥 Mijozlar ro'yxati
@router.callback_query(F.data == "clients")
async def clients_list(callback: CallbackQuery):
    await callback.answer()

    pool = callback.bot.get("db")

    async with pool.acquire() as conn:
        users = await conn.fetch("""
            SELECT telegram_id
            FROM users
            WHERE is_active = TRUE
            ORDER BY id DESC
        """)

    if not users:
        await callback.message.answer("❌ Hozircha mijozlar yo'q.")
        return

    # Inline list yaratish
    keyboard = []

    for user in users:
        uid = user["telegram_id"]
        keyboard.append([
            InlineKeyboardButton(
                text=f"👤 {uid}",
                callback_data=f"client_{uid}"
            )
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.answer(
        "👥 Mijozlar ro'yxati:",
        reply_markup=markup
    )


# 👤 Mijoz kartasi
@router.callback_query(F.data.startswith("client_"))
async def client_card(callback: CallbackQuery):
    await callback.answer()

    user_id = int(callback.data.split("_")[1])
    pool = callback.bot.get("db")

    async with pool.acquire() as conn:

        used = await conn.fetchval("""
            SELECT COALESCE(SUM(amount),0)
            FROM usage
            WHERE user_id=$1 AND confirmed=TRUE
        """, user_id)

        paid = await conn.fetchval("""
            SELECT COALESCE(SUM(amount),0)
            FROM payments
            WHERE user_id=$1
        """, user_id)

    left = used - paid

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Ishlatish", callback_data=f"use_{user_id}")],
        [InlineKeyboardButton(text="💰 To'lash", callback_data=f"pay_{user_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="clients")]
    ])

    await callback.message.answer(
        f"👤 Mijoz: {user_id}\n\n"
        f"📦 Jami ishlatilgan: {used}\n"
        f"💰 To'langan: {paid}\n"
        f"📊 Qolgan: {left}",
        reply_markup=keyboard
  )

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import AddUsage
from keyboards import confirm_keyboard

router = Router()

# ➕ Ishlatish tugmasi
@router.callback_query(F.data.startswith("use_"))
async def start_usage(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user_id = int(callback.data.split("_")[1])

    # user_id ni state ga saqlaymiz
    await state.update_data(target_user=user_id)
    await state.set_state(AddUsage.waiting_for_amount)

    await callback.message.answer("📦 Nechta dona ishlatildi?")


# 📩 Miqdor qabul qilish
@router.message(AddUsage.waiting_for_amount)
async def process_usage_amount(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    amount = int(message.text)
    data = await state.get_data()
    user_id = data["target_user"]

    pool = message.bot.get("db")

    async with pool.acquire() as conn:

        result = await conn.fetchrow("""
            INSERT INTO usage (user_id, amount)
            VALUES ($1, $2)
            RETURNING id
        """, user_id, amount)

    usage_id = result["id"]

    # Mijozga tasdiqlash yuboramiz
    await message.bot.send_message(
        user_id,
        f"📦 Siz {amount} dona ishlatdingiz.\nTasdiqlaysizmi?",
        reply_markup=confirm_keyboard(usage_id)
    )

    await message.answer("✅ Mijozga yuborildi. Tasdiq kutilmoqda.")

    await state.clear()


# ✅ Ha
@router.callback_query(F.data.startswith("confirm_"))
async def confirm_usage(callback: CallbackQuery):

    usage_id = int(callback.data.split("_")[1])
    pool = callback.bot.get("db")

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE usage
            SET confirmed=TRUE
            WHERE id=$1
        """, usage_id)

    await callback.answer("Tasdiqlandi ✅")
    await callback.message.answer("✅ Ishlatish tasdiqlandi.")


# ❌ Yo‘q
@router.callback_query(F.data.startswith("deny_"))
async def deny_usage(callback: CallbackQuery):

    usage_id = int(callback.data.split("_")[1])
    pool = callback.bot.get("db")

    async with pool.acquire() as conn:
        await conn.execute("""
            DELETE FROM usage
            WHERE id=$1
        """, usage_id)

    await callback.answer("Rad etildi ❌")
    await callback.message.answer("❌ Ishlatish rad etildi.")

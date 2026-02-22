from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import AddPayment

router = Router()

# 💰 To‘lash tugmasi
@router.callback_query(F.data.startswith("pay_"))
async def start_payment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user_id = int(callback.data.split("_")[1])

    await state.update_data(target_user=user_id)
    await state.set_state(AddPayment.waiting_for_amount)

    await callback.message.answer("💰 Nechta dona to‘lov qilindi?")


# 📩 To‘lov miqdori
@router.message(AddPayment.waiting_for_amount)
async def process_payment_amount(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    amount = int(message.text)
    data = await state.get_data()
    user_id = data["target_user"]

    pool = message.bot.get("db")

    async with pool.acquire() as conn:

        await conn.execute("""
            INSERT INTO payments (user_id, amount)
            VALUES ($1, $2)
        """, user_id, amount)

    # Mijozga xabar
    await message.bot.send_message(
        user_id,
        f"💰 Siz {amount} dona to‘lov qildingiz."
    )

    await message.answer("✅ To‘lov saqlandi.")

    await state.clear()

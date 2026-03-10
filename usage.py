import asyncpg
from aiogram import types
from aiogram.fsm.context import FSMContext

from config import DATABASE_URL


async def use_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    user_id = data["user_id"]
    amount = int(message.text)

    conn = await asyncpg.connect(DATABASE_URL)

    client = await conn.fetchrow("""
        SELECT confirmed_amount, used_amount
        FROM clients
        WHERE user_id=$1
    """, user_id)

    confirmed = client["confirmed_amount"]
    used = client["used_amount"]

    # 🔥 TEKSHIRUV
    if used + amount > confirmed:

        remaining = confirmed - used

        await message.answer(
            f"❌ Xatolik!\n"
            f"📦 Mijozda faqat {remaining} ta mahsulot qolgan."
        )

        await conn.close()
        return

    # UPDATE
    await conn.execute("""
        UPDATE clients
        SET used_amount = used_amount + $1
        WHERE user_id=$2
    """, amount, user_id)

    client = await conn.fetchrow("""
        SELECT confirmed_amount, used_amount
        FROM clients
        WHERE user_id=$1
    """, user_id)

    await conn.close()

    remaining = client["confirmed_amount"] - client["used_amount"]

    await message.answer(
        f"📉 Ishlatildi: {amount}\n"
        f"📦 Tayyor qolgani: {remaining}"
    )

    await state.clear()
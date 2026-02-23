import asyncpg
import os
from aiogram import types

ADMIN_ID = int(os.getenv("ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")


async def report_handler(message: types.Message):

    conn = await asyncpg.connect(DATABASE_URL)

    # ===== ADMIN =====
    if message.from_user.id == ADMIN_ID:

        rows = await conn.fetch("SELECT name, confirmed_amount, payments FROM clients")

        text = "📊 HISOBOT (Barcha mijozlar)\n\n"

        for row in rows:
            balance = row["confirmed_amount"] - row["payments"]
            text += (
                f"👤 {row['name']}\n"
                f"📦 Tasdiqlangan: {row['confirmed_amount']}\n"
                f"💰 To‘lov: {row['payments']}\n"
                f"📊 Qoldiq: {balance}\n\n"
            )

        await message.answer(text)

    # ===== CLIENT =====
    else:

        row = await conn.fetchrow(
            "SELECT name, confirmed_amount, payments FROM clients WHERE user_id=$1",
            message.from_user.id
        )

        if row:
            balance = row["confirmed_amount"] - row["payments"]

            await message.answer(
                f"📊 SIZNING HISOBINGIZ\n\n"
                f"📦 Tasdiqlangan: {row['confirmed_amount']}\n"
                f"💰 To‘lov: {row['payments']}\n"
                f"📊 Qoldiq: {balance}"
            )

    await conn.close()
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

import database
from config import ADMIN_CODE, CLIENT_CODE

router = Router()

user_state = {}

# START
@router.message(CommandStart())
async def start(message: Message):
    user_state[message.from_user.id] = "waiting_code"
    await message.answer("Kod kiriting:")

# MAIN LOGIC
@router.message()
async def handler(message: Message):

    if not message.text:
        return

    user_id = message.from_user.id
    text = message.text
    state = user_state.get(user_id)

    pool = database.pool

    if state == "waiting_code":

        if text == ADMIN_CODE:
            user_state[user_id] = "admin"
            await message.answer("Admin kirdingiz ✅")
            return

        if text == CLIENT_CODE:
            user_state[user_id] = "waiting_name"
            await message.answer("Ismingizni yozing:")
            return

    if state == "waiting_name":

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users(telegram_id,name,role)
                VALUES($1,$2,'client')
                ON CONFLICT (telegram_id)
                DO UPDATE SET name=EXCLUDED.name
            """, user_id, text)

        user_state[user_id] = "client"
        await message.answer("Ro‘yxatdan o‘tdingiz ✅")
        return

    if state == "client" and text == "📊 Statistika":

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id=$1",
                user_id
            )

        if user:
            remaining = user["total_add"] - user["total_close"]

            await message.answer(
                f"Qo‘shilgan: {user['total_add']} dona\n"
                f"Yopilgan: {user['total_close']} dona\n"
                f"Qolgan: {remaining} dona"
            )
        return
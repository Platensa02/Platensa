from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from config import ADMIN_CODE, CLIENT_CODE
from keyboards import admin_menu, client_menu
from states import user_state, admin_context

router = Router()


# ================= START =================

@router.message(CommandStart())
async def start(message: Message):
    user_state[message.from_user.id] = "waiting_code"
    await message.answer("Kod kiriting:")


# ================= MAIN HANDLER =================

@router.message()
async def main_handler(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id
    text = message.text
    state = user_state.get(user_id)
    pool = message.bot.dispatcher["pool"]

    # EXIT
    if text == "⬅️ Chiqish":
        user_state[user_id] = "waiting_code"
        await message.answer("Kod kiriting:")
        return

    # LOGIN
    if state == "waiting_code":

        if text == ADMIN_CODE:
            user_state[user_id] = "admin"
            await message.answer("Admin panelga xush kelibsiz ✅", reply_markup=admin_menu())
            return

        if text == CLIENT_CODE:
            user_state[user_id] = "waiting_name"
            await message.answer("Ismingizni yozing:")
            return

        await message.answer("Noto‘g‘ri kod ❌")
        return

    # SAVE CLIENT
    if state == "waiting_name":

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users(telegram_id,name,role)
                VALUES($1,$2,'client')
                ON CONFLICT (telegram_id)
                DO UPDATE SET name=EXCLUDED.name
            """, user_id, text)

        user_state[user_id] = "client"
        await message.answer("Ro‘yxatdan o‘tdingiz ✅", reply_markup=client_menu())
        return

    # CLIENT STAT
    if state == "client" and text == "📊 Statistika":

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id=$1",
                user_id
            )

        if user:
            remaining = user["total_add"] - user["total_close"]

            await message.answer(
                f"📦 Qo‘shilgan: {user['total_add']} dona\n"
                f"📤 Yopilgan: {user['total_close']} dona\n"
                f"📊 Qolgan: {remaining} dona"
            )
        return

    # ADMIN VIEW CLIENTS
    if state == "admin" and text == "📋 Mijozlar":

        async with pool.acquire() as conn:
            users = await conn.fetch("SELECT * FROM users WHERE role='client'")

        if not users:
            await message.answer("Mijozlar yo‘q.")
            return

        result = "📋 Mijozlar ro‘yxati:\n\n"

        for u in users:
            remaining = u["total_add"] - u["total_close"]
            result += f"ID:{u['id']} | {u['name']} | Qoldiq:{remaining}\n"

        await message.answer(result)
        return
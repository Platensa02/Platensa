import asyncio
import os
import asyncpg

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_CODE = "1111"
CLIENT_CODE = "2222"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ---------------- DATABASE ----------------

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# ---------------- KEYBOARDS ----------------

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Mijozlar")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Statistika")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def action_keyboard(user_id, action, amount):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"{action}_yes_{user_id}_{amount}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"{action}_no_{user_id}_{amount}"
                )
            ]
        ]
    )

# ---------------- START / CODE ----------------

user_states = {}

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Kod kiriting:")
    user_states[message.from_user.id] = "waiting_code"

@router.message()
async def code_handler(message: Message):
    user_id = message.from_user.id
    pool = dp["pool"]

    # BACK
    if message.text == "⬅️ Orqaga":
        user_states[user_id] = "waiting_code"
        await message.answer("Kod kiriting:")
        return

    # CODE CHECK
    if user_states.get(user_id) == "waiting_code":

        if message.text == ADMIN_CODE:
            user_states[user_id] = "admin"
            await message.answer("Admin menyu", reply_markup=admin_menu())

        elif message.text == CLIENT_CODE:
            user_states[user_id] = "client_name"
            await message.answer("Ismingizni yozing:")

    # CLIENT NAME SAVE
    elif user_states.get(user_id) == "client_name":

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users(name, role)
                VALUES($1,'client')
            """, message.text)

        user_states[user_id] = "client"
        await message.answer("Ro‘yxatdan o‘tdingiz", reply_markup=client_menu())

# ---------------- ADMIN ----------------

@router.message(F.text == "Mijozlar")
async def clients_list(message: Message):
    pool = dp["pool"]

    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT * FROM users WHERE role='client'")

    if not users:
        await message.answer("Mijoz yo‘q")
        return

    text = "Mijozlar:\n\n"
    for u in users:
        remaining = u["total_add"] - u["total_close"]
        text += f"{u['id']}. {u['name']} | Qolgan: {remaining}\n"

    text += "\nQo‘shish yoki yopish uchun mijoz ID sini yozing:"
    await message.answer(text)

# ---------------- ADD / CLOSE ----------------

@router.message()
async def admin_actions(message: Message):
    pool = dp["pool"]
    user_id = message.from_user.id

    if user_states.get(user_id) != "admin":
        return

    if not message.text.isdigit():
        return

    target_id = int(message.text)

    await message.answer(
        "Nechta dona?",
    )

    user_states[user_id] = f"action_{target_id}"

@router.message()
async def quantity_handler(message: Message):
    pool = dp["pool"]
    user_id = message.from_user.id

    state = user_states.get(user_id)

    if not state or not state.startswith("action_"):
        return

    if not message.text.isdigit():
        return

    target_id = int(state.split("_")[1])
    amount = int(message.text)

    # ASK CONFIRMATION (ADD EXAMPLE)
    await message.answer(
        "Tasdiqlaysizmi?",
        reply_markup=action_keyboard(target_id, "add", amount)
    )

# ---------------- CALLBACK ----------------

@router.callback_query(F.data.startswith("add_"))
async def confirm_add(call: CallbackQuery):
    pool = dp["pool"]
    _, decision, target_id, amount = call.data.split("_")
    target_id = int(target_id)
    amount = int(amount)

    if decision == "yes":
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET total_add = total_add + $1 WHERE id=$2",
                amount, target_id
            )

        await call.message.answer("Qo‘shildi")

    else:
        await call.message.answer("Rad etildi")

    await call.answer()

# ---------------- MAIN ----------------

async def main():
    pool = await create_pool()
    dp["pool"] = pool

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            name TEXT,
            role TEXT,
            total_add INTEGER DEFAULT 0,
            total_close INTEGER DEFAULT 0
        )
        """)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
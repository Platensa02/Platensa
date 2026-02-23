import asyncpg
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# Global variables (main.py dan beriladi)
bot = None
ADMIN_ID = None
DATABASE_URL = None


def setup(dp, bot_instance):
    global bot, ADMIN_ID, DATABASE_URL
    bot = bot_instance
    ADMIN_ID = int(bot_instance.token and __import__("os").getenv("ADMIN_ID"))
    DATABASE_URL = __import__("os").getenv("DATABASE_URL")

    # handlers register
    dp.message(Command("start"))(start)
    dp.message(F.text == "📦 Mahsulot qo‘shish")(add_product_start)
    dp.message(AddProduct.amount)(add_amount)
    dp.callback_query(F.data.startswith("confirm_"))(confirm_product)
    dp.callback_query(F.data == "cancel")(cancel_product)


# =====================
# STATES
# =====================
class AddProduct(StatesGroup):
    user_id = State()
    amount = State()


# =====================
# START
# =====================
async def start(message: types.Message):

    user = message.from_user

    if user.id == ADMIN_ID:
        await message.answer("Admin panel:", reply_markup=admin_menu())
        return

    conn = await asyncpg.connect(DATABASE_URL)

    client = await conn.fetchrow(
        "SELECT * FROM clients WHERE user_id=$1",
        user.id
    )

    if not client:
        await conn.execute(
            "INSERT INTO clients (user_id, name) VALUES ($1, $2)",
            user.id,
            user.full_name
        )

        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi mijoz qo‘shildi:\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}"
        )

    await conn.close()

    await message.answer("Bot ishlayapti ✅")


# =====================
# ADMIN MENU
# =====================
def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Mahsulot qo‘shish")],
            [KeyboardButton(text="💰 To‘lov kiritish")],
            [KeyboardButton(text="📊 Hisobot")]
        ],
        resize_keyboard=True
    )


# =====================
# ADD PRODUCT FLOW
# =====================
async def add_product_start(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("Mijoz Telegram ID sini yuboring:")
    await state.set_state(AddProduct.user_id)


async def add_amount(message: types.Message, state: FSMContext):

    await state.update_data(user_id=int(message.text))
    await message.answer("Miqdorni yozing:")
    await state.set_state(AddProduct.amount)


async def add_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    amount = int(message.text)
    user_id = data["user_id"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"confirm_{user_id}_{amount}"
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="cancel"
            )
        ]
    ])

    await bot.send_message(
        user_id,
        f"📦 Sizga {amount} dona qo‘shildi.\nTasdiqlaysizmi?",
        reply_markup=keyboard
    )

    await message.answer("Yuborildi ✅")
    await state.clear()


# =====================
# CONFIRM
# =====================
async def confirm_product(callback: types.CallbackQuery):

    _, user_id, amount = callback.data.split("_")

    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        UPDATE clients
        SET confirmed_amount = confirmed_amount + $1
        WHERE user_id=$2
    """, int(amount), int(user_id))

    await conn.close()

    await callback.message.edit_text("✅ Tasdiqlandi!")
    await callback.answer()


# =====================
# CANCEL
# =====================
async def cancel_product(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Bekor qilindi")
    await callback.answer()
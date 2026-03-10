import os
import asyncpg
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

class AddProduct(StatesGroup):
    amount = State()

def setup_add_product_handlers(dp, bot):

    # Mahsulot qo‘shish tugmasi
    dp.message(F.text == "📦 Mahsulot qo‘shish")(lambda msg: add_product_start(msg, bot))

    # Callback va FSM
    dp.callback_query(F.data.startswith("select_"))(lambda cb: select_client(cb, bot, dp))
    dp.callback_query(
        F.data.startswith("confirm_") &
        ~F.data.startswith("confirm_delete_")
    )(lambda cb: confirm_product(cb, bot))
    dp.callback_query(F.data == "cancel")(lambda cb: cancel_product(cb, bot))
    dp.message(AddProduct.amount)(lambda msg: get_amount(msg, bot, dp))


async def add_product_start(message: types.Message, bot):
    if message.from_user.id != ADMIN_ID:
        return
    conn = await asyncpg.connect(DATABASE_URL)
    clients = await conn.fetch("SELECT user_id, name FROM clients")
    await conn.close()

    keyboard = [[InlineKeyboardButton(text=c["name"], callback_data=f"select_{c['user_id']}")] for c in clients]

    await message.answer(
        "Mijozni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


async def select_client(callback, bot, dp):
    from aiogram.fsm.context import FSMContext
    state: FSMContext = dp.current_state(chat=callback.message.chat.id, user=callback.from_user.id)
    user_id = int(callback.data.split("_")[1])
    await state.update_data(user_id=user_id)
    await callback.message.answer("Miqdorni yozing:")
    await state.set_state(AddProduct.amount)
    await callback.answer()


async def get_amount(message, bot, dp):
    from aiogram.fsm.context import FSMContext
    state: FSMContext = dp.current_state(chat=message.chat.id, user=message.from_user.id)
    data = await state.get_data()
    user_id = data["user_id"]
    amount = int(message.text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_{user_id}_{amount}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")
        ]
    ])
    await bot.send_message(user_id, f"📦 Sizga {amount} dona qo‘shildi.\nTasdiqlaysizmi?", reply_markup=keyboard)
    await message.answer("Mijozga yuborildi ✅")
    await state.clear()


async def confirm_product(callback, bot):
    if not callback.data.startswith("confirm_"):
        return
    _, user_id, amount = callback.data.split("_")
    user_id, amount = int(user_id), int(amount)
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("UPDATE clients SET confirmed_amount = confirmed_amount + $1 WHERE user_id=$2", amount, user_id)
    client = await conn.fetchrow("SELECT name FROM clients WHERE user_id=$1", user_id)
    await conn.close()
    name = client["name"] if client else "Noma’lum"
    await bot.send_message(user_id, f"✅ Tasdiqlandi!\n📦 Qo‘shildi: {amount} dona")
    await bot.send_message(ADMIN_ID, f"📢 Tasdiqlandi\n👤 Ism: {name}\n📦 Miqdor: {amount}")
    await callback.message.edit_text("✅ Tasdiqlandi!")
    await callback.answer()


async def cancel_product(callback, bot):
    await bot.send_message(ADMIN_ID, "❌ Mijoz mahsulotni rad etdi.")
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()
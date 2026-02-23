from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mijozlar")],
            [KeyboardButton(text="➕ Qo‘shish")],
            [KeyboardButton(text="➖ Yopish")],
            [KeyboardButton(text="⬅️ Chiqish")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="⬅️ Chiqish")]
        ],
        resize_keyboard=True
    )
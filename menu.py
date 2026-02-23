from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Mahsulot qo‘shish")],
            [KeyboardButton(text="💰 To‘lov kiritish")],
            [KeyboardButton(text="📊 Hisobot")]
        ],
        resize_keyboard=True
    )

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Hisobot")]
        ],
        resize_keyboard=True
    )
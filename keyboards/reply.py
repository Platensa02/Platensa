from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =========================
# 👨‍💼 ADMIN MENYU
# =========================
def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Mijozlar")],
            [KeyboardButton(text="➕ Mijoz qo‘shish")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Admin panel"
    )


# =========================
# 👤 MIJOZ MENYU
# =========================
def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Jami ishlatganim")],
            [KeyboardButton(text="📊 Qolganim")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Mijoz panel"
    )
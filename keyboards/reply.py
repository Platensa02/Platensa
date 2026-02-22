from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =========================
# 🔙 ORQAGA TUGMASI
# =========================
def back_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )


# =========================
# 👨‍💼 ADMIN BOSH MENYU
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
# 👤 MIJOZ BOSH MENYU
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
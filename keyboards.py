from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# 👨‍💼 ADMIN MENYU
def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ Mijoz qo‘shish",
                callback_data="add_client"
            )
        ],
        [
            InlineKeyboardButton(
                text="👥 Mijozlar",
                callback_data="clients"
            )
        ]
    ])


# 👤 MIJOZ MENYU
def client_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📦 Jami ishlatganim",
                callback_data="my_used"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Qolganim",
                callback_data="my_left"
            )
        ]
    ])


# 🔔 TASDIQLASH
def confirm_keyboard(usage_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Ha",
                callback_data=f"confirm_{usage_id}"
            ),
            InlineKeyboardButton(
                text="❌ Yo'q",
                callback_data=f"deny_{usage_id}"
            )
        ]
    ])


# 🔙 ORQAGA (admin panelga qaytish uchun)
def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="clients"
            )
        ]
    ])
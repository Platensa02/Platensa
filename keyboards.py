from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ADMIN MENYU
def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Mijozlar", callback_data="clients")]
    ])

# MIJOZ MENYU (FAQAT 2 TA TUGMA)
def client_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Jami ishlatganim", callback_data="my_used")],
        [InlineKeyboardButton(text="📊 Qolganim", callback_data="my_left")]
    ])

# ORQAGA
def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")]
    ])

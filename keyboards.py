from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ADMIN BOSHLANG'ICH MENYU
def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Mijozlar", callback_data="clients")],
        [InlineKeyboardButton(text="➕ Mijoz qo'shish", callback_data="add_client")]
    ])

# ORQAGA TUGMA
def back_button(data="back"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data=data)]
    ])

# MIJOZ ICHKI MENYU
def client_menu(client_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Ishlatish", callback_data=f"use_{client_id}")],
        [InlineKeyboardButton(text="💰 To'lash", callback_data=f"pay_{client_id}")],
        [InlineKeyboardButton(text="📊 Hisobot", callback_data=f"report_{client_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="clients")]
    ])

# ISHLATISH TASDIQLASH
def confirm_usage(usage_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_{usage_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=f"deny_{usage_id}")
        ]
    ])

# MIJOZ PANEL (2 TA TUGMA)
def client_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Jami ishlatganim", callback_data="my_used")],
        [InlineKeyboardButton(text="📊 Qolganim", callback_data="my_left")]
    ])

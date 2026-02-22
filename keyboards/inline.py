from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# =========================
# ➕ ISHLATISH TASDIQLASH
# =========================
def confirm_usage_keyboard(usage_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha",
                    callback_data=f"confirm_{usage_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Yo‘q",
                    callback_data=f"reject_{usage_id}"
                )
            ]
        ]
    )


# =========================
# 👤 MIJOZ TANLASH
# =========================
def clients_list_keyboard(clients):
    buttons = []

    for client in clients:
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {client['telegram_id']}",
                callback_data=f"client_{client['id']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# 👤 MIJOZ KARTASI TUGMALARI
# =========================
def client_actions_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Ishlatish",
                    callback_data=f"add_usage_{user_id}"
                ),
                InlineKeyboardButton(
                    text="💰 To‘lash",
                    callback_data=f"add_payment_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 O‘chirish",
                    callback_data=f"delete_user_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back"
                )
            ]
        ]
    )
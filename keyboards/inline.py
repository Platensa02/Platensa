from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_keyboard(action, user_id, amount):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"{action}|yes|{user_id}|{amount}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"{action}|no|{user_id}|{amount}"
                )
            ]
        ]
    )
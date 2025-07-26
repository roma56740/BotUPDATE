from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

admin_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Все пользователи"), KeyboardButton(text="Удалить пользователя")],
        [KeyboardButton(text="План продаж"), KeyboardButton(text="Все менеджеры")],
        [KeyboardButton(text="Добавить сердце"), KeyboardButton(text="Снять сердце")]
    ],
    resize_keyboard=True
)

def get_decision_keyboard(approve_data: str, decline_data: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=approve_data),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=decline_data),
            ]
        ]
    )

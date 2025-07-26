from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

manager_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Помог коллеге")],
        [KeyboardButton(text="Моя статистика")]
    ],
    resize_keyboard=True
)

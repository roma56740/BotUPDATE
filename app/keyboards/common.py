from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Склад")],
        [KeyboardButton(text="Бухгалтер")],
        [KeyboardButton(text="Менеджер")]
    ],
    resize_keyboard=True
)

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Помог коллеге")]
    ],
    resize_keyboard=True
)

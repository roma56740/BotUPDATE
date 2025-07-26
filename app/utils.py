from aiogram.types import Message
from app.database import get_user_by_username

def format_user_info(user):
    if not user:
        return "Пользователь не найден."
    user_id, username, role, name, hearts, penalty = user
    return (
        f"👤 Имя: {name}\n"
        f"🔹 Роль: {role}\n"
        f"🔸 Username: @{username}\n"
        f"❤️ Сердец: {hearts}/3\n"
        f"⚠️ Штраф: {penalty}"
    )

async def notify_user_by_username(bot, username, text):
    user = get_user_by_username(username)
    if user:
        user_id = user[0]
        await bot.send_message(user_id, text)
    
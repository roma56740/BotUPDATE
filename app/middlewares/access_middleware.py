from aiogram import BaseMiddleware
from aiogram.types import Message
from app.config import ADMIN_ID

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if event.from_user.id != ADMIN_ID:
            await event.answer("⛔ Доступ запрещен.")
            return
        return await handler(event, data)

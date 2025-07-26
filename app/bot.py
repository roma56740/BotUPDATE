import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN
from app.handlers import user_router, admin_router, notify
from app.middlewares.access_middleware import AdminMiddleware
from app.database import init_db

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Инициализация базы данных
    init_db()

    # Подключаем роутеры
    dp.include_router(user_router.user_router)

    # Применяем middleware ТОЛЬКО к admin_router
    admin_router.admin_router.message.middleware(AdminMiddleware())
    dp.include_router(admin_router.admin_router)

    # Планировщик уведомлений (ежедневно)
    notify.setup_scheduler(bot)

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

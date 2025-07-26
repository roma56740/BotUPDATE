from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import get_all_users
from app.utils import format_user_info
from app.config import ADMIN_ID
import datetime

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    @scheduler.scheduled_job("cron", hour=11, minute=30, day_of_week="mon-fri")
    async def daily_report():
        users = get_all_users()
        text = "📋 Ежедневный отчёт:\n\n"
        for u in users:
            text += format_user_info(u) + "\n\n"
        await bot.send_message(ADMIN_ID, text)

    @scheduler.scheduled_job("cron", hour=21, minute=0)
    async def nightly_notify():
        users = get_all_users()
        for u in users:
            user_id = u[0]
            hearts = u[4]
            penalty = u[5]
            text = f"❤️ Сердец: {hearts}/3\n⚠️ Штраф: {penalty}"
            await bot.send_message(user_id, "⏰ Напоминание:\n" + text)

    scheduler.start()

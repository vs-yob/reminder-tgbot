from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.redis import RedisJobStore
from aiogram import Bot
from db.models.models import Reminder, RepeatType
from tortoise import Tortoise


class ReminderScheduler:
    def __init__(self, bot: Bot, jobstores=None):
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        self.bot = bot

    async def start(self):
        self.scheduler.start()
        # При запуске не нужно вручную планировать задачи,
        # так как APScheduler автоматически восстановит их из Redis

    async def schedule_reminder(self, reminder: Reminder):
        job_id = f"reminder_{reminder.id}"
        
        # Schedule the initial notification
        self.scheduler.add_job(
            self._send_reminder,
            'date',
            run_date=reminder.remind_at,
            args=[reminder.id],
            id=job_id
        )

        # If reminder is repeating, schedule the next occurrence
        if reminder.repeat != RepeatType.NONE:
            self._schedule_repeat(reminder)

    def _schedule_repeat(self, reminder: Reminder):
        job_id = f"reminder_{reminder.id}_repeat"
        
        if reminder.repeat == RepeatType.DAILY:
            trigger = CronTrigger(hour=reminder.remind_at.hour, minute=reminder.remind_at.minute)
        elif reminder.repeat == RepeatType.WEEKLY:
            trigger = CronTrigger(
                day_of_week=reminder.remind_at.strftime('%a').lower(),
                hour=reminder.remind_at.hour,
                minute=reminder.remind_at.minute
            )
        else:
            return

        self.scheduler.add_job(
            self._send_reminder,
            trigger=trigger,
            args=[reminder.id],
            id=job_id
        )

    async def _send_reminder(self, reminder_id: int):
        reminder = await Reminder.get_or_none(id=reminder_id)
        if not reminder or not reminder.is_active:
            return

        user = await reminder.user
        await self.bot.send_message(
            chat_id=user.telegram_id,
            text=f"⏰ Reminder: {reminder.text}"
        )

        # If it's a one-time reminder, deactivate it
        if reminder.repeat == RepeatType.NONE:
            reminder.is_active = False
            await reminder.save()

    async def remove_reminder(self, reminder_id: int):
        job_id = f"reminder_{reminder_id}"
        repeat_job_id = f"reminder_{reminder_id}_repeat"
        
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        if self.scheduler.get_job(repeat_job_id):
            self.scheduler.remove_job(repeat_job_id) 
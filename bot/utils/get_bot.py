from aiogram import Bot
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore




default_jobstores = {
    'default': RedisJobStore(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=int(os.getenv("REDIS_DB") or 0)
        )
}
bot = Bot(token=os.getenv("BOT_TOKEN"))  # type: ignore
scheduler = AsyncIOScheduler(jobstores=default_jobstores)

def get_bot():
    return bot

def get_scheduler():
    return scheduler




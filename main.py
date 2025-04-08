import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from dotenv import load_dotenv
from tortoise import Tortoise
import os
import redis.asyncio as redis

from db.config import TORTOISE_ORM, RedisSettings
from db.models.models import User, Reminder
from bot.handlers.handlers import router, scheduler
from scheduler.scheduler import ReminderScheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Initialize Redis
    redis_settings = RedisSettings()
    redis_client = redis.Redis(
        host=redis_settings.REDIS_HOST,
        port=redis_settings.REDIS_PORT,
        db=redis_settings.REDIS_DB,
        decode_responses=True
    )
    
    # Initialize bot and dispatcher with Redis storage
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)
    
    # Initialize scheduler with Redis job store
    jobstores = {
        'default': RedisJobStore(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            db=redis_settings.REDIS_DB
        )
    }
    
    # Initialize scheduler
    global scheduler
    scheduler = ReminderScheduler(bot, jobstores=jobstores)
    
    # Initialize database
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    # Start scheduler
    await scheduler.start()
    
    # Register handlers
    dp.include_router(router)
    
    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await Tortoise.close_connections()
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())

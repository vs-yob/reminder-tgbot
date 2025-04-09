import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from tortoise import Tortoise
import redis.asyncio as redis
from bot.middlewares.scheduler_middleware import SchedulerMiddleware
from db.config import redis_settings
from bot.handlers.handlers import router
from bot.utils.get_bot import get_bot, get_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Initialize Redis
    redis_client = redis.Redis(
        host=redis_settings.REDIS_HOST,
        port=redis_settings.REDIS_PORT,
        db=redis_settings.REDIS_DB,
        decode_responses=True
    )
    
    # Initialize bot and dispatcher with Redis storage
    
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)
    
    # Initialize scheduler with Redis job store

    
    # Initialize scheduler
    scheduler = get_scheduler()
    
    # Initialize database
    await Tortoise.init(
        db_url="sqlite:///db.sqlite3",
        _create_db=True,
        use_tz=True, 
        timezone=redis_settings.TIMEZONE, 
        modules={"models": ["db.models.models"]},
        
    )
    await Tortoise.generate_schemas(safe=True)
    
    # Start scheduler
    await scheduler.start()
    scheduler_middleware = SchedulerMiddleware(scheduler)
    router.message.middleware(scheduler_middleware)
    router.callback_query.middleware(scheduler_middleware)
    # Register handlers
    dp.include_router(router)
    
    bot = get_bot()
    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await Tortoise.close_connections()
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())

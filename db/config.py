import os
from typing import List
from pydantic import BaseModel


class RedisSettings(BaseModel):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    BOT_TOKEN: str
    TIMEZONE: str = "UTC"


redis_settings = RedisSettings(
    REDIS_HOST=os.getenv("REDIS_HOST"),  # type: ignore
    REDIS_PORT=os.getenv("REDIS_PORT"),  # type: ignore
    REDIS_DB=os.getenv("REDIS_DB"),  # type: ignore
    BOT_TOKEN=os.getenv("BOT_TOKEN"),  # type: ignore
)


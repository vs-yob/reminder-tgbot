
from typing import Any, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.utils.get_bot import get_scheduler

class SchedulerMiddleware(BaseMiddleware):
    def __init__(self):    
        self.scheduler = get_scheduler()


    async def __call__(self, handler: Callable, event: Message | CallbackQuery, data: dict[str, Any]):
        data["scheduler"] = self.scheduler
        return await handler(event, data)


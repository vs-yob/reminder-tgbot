from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.models.models import User, Reminder, RepeatType
from bot.keyboards.keyboards import (
    get_main_keyboard,
    get_repeat_keyboard,
    get_reminder_actions_keyboard,
    get_reminders_list_keyboard
)
from bot.utils.date_parser import parse_datetime, parse_reminder_text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.utils.job_functions import send_reminder
router = Router()



MSG_TXT = """
Введіть текст нагадування.


Ви можете вказати дату та час прямо в тексті:
- завтра о 15:00
- післязавтра о 12:00
- в понеділок о 18:30
- сьогодні о півночі
- 09.04.2025 23:00

Або використайте спеціальний формат:
date#09.04.2025 time#23:00 repeat#daily

Також можна вказати періодичність:
- щоденно
- щотижня
- без повторення
"""


class ReminderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()
    waiting_for_repeat = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user, _ = await User.get_or_create(telegram_id=message.from_user.id)
    await message.answer(     
        "👋 Вітаю в боті нагадувань!\n\n"
        "Використовуйте клавіатуру нижче для керування нагадуваннями:",
        reply_markup=get_main_keyboard()
    )


@router.callback_query(F.data == "add_reminder")
async def add_reminder(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReminderStates.waiting_for_text)
    await callback.message.edit_text(MSG_TXT)


@router.message(ReminderStates.waiting_for_text)
async def process_reminder_text(message: Message, state: FSMContext, scheduler: AsyncIOScheduler):
    if not message.text:
        await message.answer("Будь ласка, введіть текст нагадування.")
        return
    
    # Парсимо текст нагадування
    parsed = parse_reminder_text(message.text)
    
    
    # Якщо знайдено дату та час
    if parsed["remind_at"]:
        if parsed["remind_at"] < datetime.now():
            await message.answer("Будь ласка, введіть майбутню дату та час!")
            return
            
        user = await User.get(telegram_id=message.from_user.id)
        reminder = await Reminder.create(
            user=user,
            **parsed
        )
            
        job = scheduler.add_job(send_reminder, name=f"user:{user.telegram_id}:task_id:{reminder.id}", trigger='date', run_date=parsed["remind_at"], args=[reminder.id])
        await message.answer(
            f"✅ Нагадування створено успішно!\n\n"
            f"Текст: {parsed['text']}\n"
            f"Час: {parsed['remind_at'].strftime('%d.%m.%Y %H:%M')}\n"
            f"Періодичність: {parsed['repeat'].value}"
        )
            
        # Якщо періодичність не вказана, запитуємо її
        await state.set_state(ReminderStates.waiting_for_repeat)
        await message.answer(
            "Виберіть періодичність нагадування:",
            reply_markup=get_repeat_keyboard()
        )
        return
    
    # Якщо дата не знайдена, запитуємо її
    await state.set_state(ReminderStates.waiting_for_time)
    await message.answer(
        "Введіть дату та час нагадування.\n\n"
        "Приклади:\n"
        "- завтра о 15:00\n"
        "- післязавтра о 12:00\n"
        "- в понеділок о 18:30\n"
        "- сьогодні о півночі\n"
        "- 09.04.2025 23:00"
    )


@router.message(ReminderStates.waiting_for_time)
async def process_reminder_time(message: Message, state: FSMContext, scheduler: AsyncIOScheduler):
    if not message.text:
        await message.answer("Будь ласка, введіть дату та час.")
        return
        
    remind_at = parse_datetime(message.text)
    if not remind_at:
        await message.answer(
            "Не вдалося розпізнати дату та час. Спробуйте ще раз.\n\n"
            "Приклади:\n"
            "- завтра о 15:00\n"
            "- післязавтра о 12:00\n"
            "- в понеділок о 18:30\n"
            "- сьогодні о півночі\n"
            "- 09.04.2025 23:00"
        )
        return

    if remind_at < datetime.now():
        await message.answer("Будь ласка, введіть майбутню дату та час!")
        return

    # Зберігаємо дату як рядок ISO формату
    await state.update_data(remind_at=remind_at.isoformat())
    await state.set_state(ReminderStates.waiting_for_repeat)
    await message.answer(
        "Виберіть періодичність нагадування:",
        reply_markup=get_repeat_keyboard()
    )


@router.callback_query(F.data.startswith("repeat_"))
async def process_repeat_option(callback: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    repeat_type = callback.data.split("_")[1]
    data = await state.get_data()
    
    user = await User.get(telegram_id=callback.from_user.id)
    reminder = await Reminder.create(
        user=user,
        text=data["text"],
        remind_at=datetime.fromisoformat(data["remind_at"]),
        repeat=RepeatType(repeat_type)
    )

    await scheduler.schedule_reminder(reminder)
    await callback.message.edit_text(
        f"✅ Нагадування створено успішно!\n\n"
        f"Текст: {data['text']}\n"
        f"Час: {datetime.fromisoformat(data['remind_at']).strftime('%d.%m.%Y %H:%M')}\n"
        f"Періодичність: {repeat_type}"
    )
    await state.clear()


@router.callback_query(F.data == "list_reminders")
async def list_reminders(callback: CallbackQuery):
    user = await User.get(telegram_id=callback.from_user.id)
    reminders = await Reminder.filter(user=user, is_active=True)
    
    if not reminders:
        await callback.message.edit_text("У вас немає активних нагадувань.")
        return

    await callback.message.edit_text(
        "Ваші активні нагадування:",
        reply_markup=get_reminders_list_keyboard(reminders)
    )


@router.callback_query(F.data.startswith("reminder_"))
async def show_reminder_details(callback: CallbackQuery):
    reminder_id = int(callback.data.split("_")[1])
    reminder = await Reminder.get_or_none(id=reminder_id)
    
    if not reminder:
        await callback.message.edit_text("Нагадування не знайдено.")
        return

    await callback.message.edit_text(
        f"Деталі нагадування:\n\n"
        f"Текст: {reminder.text}\n"
        f"Час: {reminder.remind_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"Періодичність: {reminder.repeat.value}",
        reply_markup=get_reminder_actions_keyboard(reminder.id)
    )


@router.callback_query(F.data.startswith("delete_"))
async def delete_reminder(callback: CallbackQuery, scheduler: AsyncIOScheduler):
    reminder_id = int(callback.data.split("_")[1])
    reminder = await Reminder.get_or_none(id=reminder_id)
    
    if not reminder:
        await callback.message.edit_text("Нагадування не знайдено.")
        return

    await scheduler.remove_reminder(reminder.id)
    reminder.is_active = False
    await reminder.save()
    
    await callback.message.edit_text("✅ Нагадування видалено успішно!")


@router.callback_query(F.data.startswith("edit_"))
async def edit_reminder(callback: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    reminder_id = int(callback.data.split("_")[1])
    reminder = await Reminder.get_or_none(id=reminder_id)
    
    if not reminder:
        await callback.message.edit_text("Нагадування не знайдено.")
        return

    await state.update_data(reminder_id=reminder_id)
    await state.set_state(ReminderStates.waiting_for_text)
    await callback.message.edit_text(
        "Введіть новий текст нагадування.\n\n"
        "Ви можете вказати дату та час прямо в тексті:\n"
        "- завтра о 15:00\n"
        "- післязавтра о 12:00\n"
        "- в понеділок о 18:30\n"
        "- сьогодні о півночі\n"
        "- 09.04.2025 23:00\n\n"
        "Або використайте спеціальний формат:\n"
        "date#09.04.2025 time#23:00 repeat#daily\n\n"
        "Також можна вказати періодичність:\n"
        "- щоденно\n"
        "- щотижня\n"
        "- без повторення"
    ) 
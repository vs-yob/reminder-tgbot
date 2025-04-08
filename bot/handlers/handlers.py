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
from scheduler.scheduler import ReminderScheduler


router = Router()
scheduler = None


class ReminderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()
    waiting_for_repeat = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user, _ = await User.get_or_create(telegram_id=message.from_user.id)
    await message.answer(
        "👋 Welcome to the Reminder Bot!\n\n"
        "Use the keyboard below to manage your reminders:",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "📝 Add Reminder")
async def add_reminder(message: Message, state: FSMContext):
    await state.set_state(ReminderStates.waiting_for_text)
    await message.answer("Please enter the reminder text:")


@router.message(ReminderStates.waiting_for_text)
async def process_reminder_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(ReminderStates.waiting_for_time)
    await message.answer(
        "Please enter the reminder time in format 'YYYY-MM-DD HH:MM':"
    )


@router.message(ReminderStates.waiting_for_time)
async def process_reminder_time(message: Message, state: FSMContext):
    try:
        remind_at = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        if remind_at < datetime.now():
            await message.answer("Please enter a future time!")
            return

        await state.update_data(remind_at=remind_at)
        await state.set_state(ReminderStates.waiting_for_repeat)
        await message.answer(
            "Choose repeat option:",
            reply_markup=get_repeat_keyboard()
        )
    except ValueError:
        await message.answer("Invalid date format. Please use 'YYYY-MM-DD HH:MM'")


@router.callback_query(F.data.startswith("repeat_"))
async def process_repeat_option(callback: CallbackQuery, state: FSMContext):
    repeat = callback.data.split("_")[1]
    data = await state.get_data()
    
    user = await User.get(telegram_id=callback.from_user.id)
    reminder = await Reminder.create(
        user=user,
        text=data["text"],
        remind_at=data["remind_at"],
        repeat=repeat
    )

    await scheduler.schedule_reminder(reminder)
    await callback.message.edit_text(
        f"✅ Reminder created successfully!\n\n"
        f"Text: {data['text']}\n"
        f"Time: {data['remind_at'].strftime('%Y-%m-%d %H:%M')}\n"
        f"Repeat: {repeat}"
    )
    await state.clear()


@router.message(F.text == "📋 List Reminders")
async def list_reminders(message: Message):
    user = await User.get(telegram_id=message.from_user.id)
    reminders = await Reminder.filter(user=user, is_active=True)
    
    if not reminders:
        await message.answer("You have no active reminders.")
        return

    await message.answer(
        "Your active reminders:",
        reply_markup=get_reminders_list_keyboard(reminders)
    )


@router.callback_query(F.data.startswith("reminder_"))
async def show_reminder_details(callback: CallbackQuery):
    reminder_id = int(callback.data.split("_")[1])
    reminder = await Reminder.get_or_none(id=reminder_id)
    
    if not reminder:
        await callback.message.edit_text("Reminder not found.")
        return

    await callback.message.edit_text(
        f"Reminder details:\n\n"
        f"Text: {reminder.text}\n"
        f"Time: {reminder.remind_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"Repeat: {reminder.repeat}",
        reply_markup=get_reminder_actions_keyboard(reminder.id)
    )


@router.callback_query(F.data.startswith("delete_"))
async def delete_reminder(callback: CallbackQuery):
    reminder_id = int(callback.data.split("_")[1])
    reminder = await Reminder.get_or_none(id=reminder_id)
    
    if not reminder:
        await callback.message.edit_text("Reminder not found.")
        return

    await scheduler.remove_reminder(reminder.id)
    reminder.is_active = False
    await reminder.save()
    
    await callback.message.edit_text("✅ Reminder deleted successfully!") 
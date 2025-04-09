from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.models.models import RepeatType


def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="📝 Додати нагадування", callback_data="add_reminder"),
        InlineKeyboardButton(text="📋 Список нагадувань", callback_data="list_reminders"),
        InlineKeyboardButton(text="❌ Видалити нагадування", callback_data="delete_reminder")
    )
    keyboard.adjust(1, 2)
    return keyboard.as_markup()


def get_repeat_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Немає", callback_data=f"repeat_{RepeatType.NONE}"),
        InlineKeyboardButton(text="Щоденно", callback_data=f"repeat_{RepeatType.DAILY}"),
        InlineKeyboardButton(text="Щотижня", callback_data=f"repeat_{RepeatType.WEEKLY}")
    )
    keyboard.adjust(1, 1, 1)
    return keyboard.as_markup()


def get_reminder_actions_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="❌ Видалити", callback_data=f"delete_{reminder_id}"),
        InlineKeyboardButton(text="🔄 Редагувати", callback_data=f"edit_{reminder_id}")
    )
    keyboard.adjust(2)
    return keyboard.as_markup()


def get_reminders_list_keyboard(reminders: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for reminder in reminders:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{reminder.text[:30]}... ({reminder.remind_at.strftime('%d.%m.%Y %H:%M')})",
                callback_data=f"reminder_{reminder.id}"
            )
        )
    keyboard.adjust(1)
    return keyboard.as_markup() 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db.models.models import RepeatType


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📝 Add Reminder"))
    keyboard.add(KeyboardButton("📋 List Reminders"), KeyboardButton("❌ Delete Reminder"))
    return keyboard


def get_repeat_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("None", callback_data=f"repeat_{RepeatType.NONE}"),
        InlineKeyboardButton("Daily", callback_data=f"repeat_{RepeatType.DAILY}"),
        InlineKeyboardButton("Weekly", callback_data=f"repeat_{RepeatType.WEEKLY}")
    )
    return keyboard


def get_reminder_actions_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("❌ Delete", callback_data=f"delete_{reminder_id}"),
        InlineKeyboardButton("🔄 Edit", callback_data=f"edit_{reminder_id}")
    )
    return keyboard


def get_reminders_list_keyboard(reminders: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    for reminder in reminders:
        keyboard.add(
            InlineKeyboardButton(
                f"{reminder.text[:30]}... ({reminder.remind_at.strftime('%Y-%m-%d %H:%M')})",
                callback_data=f"reminder_{reminder.id}"
            )
        )
    return keyboard 
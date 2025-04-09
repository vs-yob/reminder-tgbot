
from db.models.models import Reminder, RepeatType
from bot.utils.get_bot import get_bot



async def send_reminder(reminder_id: int):
    bot = get_bot()
    reminder = await Reminder.get_or_none(id=reminder_id)
    if not reminder or not reminder.is_active:
        return

    user = await reminder.user
    await bot.send_message(
        chat_id=user.telegram_id, text=f"⏰ Reminder: {reminder.text}"
    )

    # If it's a one-time reminder, deactivate it
    if reminder.repeat == RepeatType.NONE:
        reminder.is_active = False
        await reminder.save()

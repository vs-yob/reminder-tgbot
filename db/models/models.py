from enum import Enum
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class RepeatType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


class User(models.Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    timezone = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"


class Reminder(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reminders")
    text = fields.TextField()
    remind_at = fields.DatetimeField(null=True, default=None)
    repeat = fields.CharEnumField(RepeatType, default=RepeatType.NONE)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "reminders"


# Create Pydantic models for API
User_Pydantic = pydantic_model_creator(User, name="User")
Reminder_Pydantic = pydantic_model_creator(Reminder, name="Reminder") 
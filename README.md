# Telegram Reminder Bot

A modern Telegram bot that brings the simplicity of Apple Reminders to your chats.  
Set tasks, get notified, stay productive — all within Telegram.

### 🚀 Features:
- 🔔 Schedule custom reminders with natural language
- 📆 Repeating tasks and reminders
- 🧠 Persistent storage using PostgreSQL + Tortoise ORM
- ⚙️ Background scheduling powered by APScheduler
- 📬 Telegram bot powered by Aiogram 3.x
- 🧪 Easily extendable for personal productivity workflows

### 🛠 Tech Stack:
- **Python**
- **Aiogram 3** — for handling Telegram Bot API
- **Tortoise ORM** — async ORM for PostgreSQL
- **APScheduler** — for scheduling reminders
- **FastAPI (optional)** — for API endpoints (e.g., mobile/web integration)

---

### 📦 Getting Started:

1. Clone the repo
2. Configure `.env` file (see `.env.example`)
3. Run migrations
4. Launch the bot

---

### 🧩 Planned Features:
- Voice reminder creation via voice-to-text
- Priority levels & color tagging
- Integration with Google Calendar

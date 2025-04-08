# Telegram Reminder Bot

A Telegram bot that helps users manage their reminders with features like scheduling, repeating reminders, and easy management through a user-friendly interface.

## Features

- Create, update, and delete reminders via Telegram chat
- Schedule reminders for specific dates and times
- Set repeating reminders (daily, weekly)
- User-friendly interface with inline keyboards
- Persistent storage using SQLite
- Redis for state management and job scheduling
- Async implementation for better performance
- Docker support for easy deployment

## Requirements

- Python 3.8+ (for local development)
- Redis (for local development)
- Docker and Docker Compose (for containerized deployment)
- Python packages (see requirements.txt)

## Setup

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd reminder-tgbot
```

2. Create a `.env` file with the following content:
```
BOT_TOKEN=your_bot_token_here
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
TIMEZONE=UTC
```

3. Run the application with Docker Compose:
```bash
docker-compose up -d
```

4. Check the logs:
```bash
docker-compose logs -f bot
```

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd reminder-tgbot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following content:
```
BOT_TOKEN=your_bot_token_here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
TIMEZONE=UTC
```

5. Install and start Redis:
```bash
# On macOS with Homebrew
brew install redis
brew services start redis

# On Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

6. Run the bot:
```bash
python main.py
```

## Usage

1. Start the bot by sending `/start`
2. Use the keyboard buttons to:
   - Add a new reminder
   - List existing reminders
   - Delete reminders
3. Follow the bot's prompts to create reminders:
   - Enter reminder text
   - Specify date and time
   - Choose repeat option (if any)

## Commands

- `/start` - Start the bot and show main menu
- The bot also responds to button clicks for:
  - Adding reminders
  - Listing reminders
  - Deleting reminders
  - Managing reminder details

## Development

The project structure is organized as follows:

```
reminder-tgbot/
├── bot/
│   ├── handlers/
│   │   └── handlers.py
│   ├── keyboards/
│   │   └── keyboards.py
│   └── middlewares/
├── db/
│   ├── models/
│   │   └── models.py
│   └── config.py
├── scheduler/
│   └── scheduler.py
├── data/           # SQLite database directory
├── .env
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

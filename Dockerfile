FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для SQLite
RUN mkdir -p /app/data && chmod 777 /app/data

# Запуск приложения
CMD ["python", "main.py"] 
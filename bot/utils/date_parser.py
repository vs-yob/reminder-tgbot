from datetime import datetime, timedelta
import re
from typing import Optional, Tuple, Dict
from db.models.models import RepeatType

# Ключові слова для розпізнавання відносних дат
RELATIVE_DAYS = {
    "сьогодні": 0,
    "завтра": 1,
    "післязавтра": 2,
    "вчора": -1,
    "позавчора": -2,
}

# Ключові слова для розпізнавання днів тижня
WEEKDAYS = {
    "понеділок": 0,
    "вівторок": 1,
    "середа": 2,
    "четвер": 3,
    "п'ятниця": 4,
    "субота": 5,
    "неділя": 6,
}

# Ключові слова для розпізнавання періодичності
REPEAT_KEYWORDS = {
    "щоденно": RepeatType.DAILY,
    "щодня": RepeatType.DAILY,
    "щотижня": RepeatType.WEEKLY,
    "щотижнево": RepeatType.WEEKLY,
    "щомісяця": None,  # Буде додано пізніше
    "щорічно": None,  # Буде додано пізніше
    "немає": RepeatType.NONE,
    "без повторення": RepeatType.NONE,
}

def parse_time(time_str: str) -> Optional[Tuple[int, int]]:
    """Парсить час з рядка у форматі HH:MM або природної мови"""
    # Спроба знайти час у форматі HH:MM
    time_pattern = r"(\d{1,2}):(\d{2})"
    match = re.search(time_pattern, time_str)
    if match:
        hours, minutes = map(int, match.groups())
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return hours, minutes
    
    # Спроба знайти час у природній мові
    time_words = {
        "полудень": (12, 0),
        "південь": (12, 0),
        "півноч": (0, 0),
        "опівночі": (0, 0),
    }
    
    for word, time in time_words.items():
        if word in time_str.lower():
            return time
    
    return None

def parse_date(date_str: str) -> Optional[datetime]:
    """Парсить дату з рядка у форматі YYYY-MM-DD або природної мови"""
    now = datetime.now()
    
    # Спроба знайти дату у форматі YYYY-MM-DD або DD.MM.YYYY
    date_patterns = [
        r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
        r"(\d{2})\.(\d{2})\.(\d{4})",  # DD.MM.YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if pattern == date_patterns[0]:
                    year, month, day = map(int, match.groups())
                else:
                    day, month, year = map(int, match.groups())
                return datetime(year, month, day)
            except ValueError:
                continue
    
    # Перевірка на відносні дати
    for word, days in RELATIVE_DAYS.items():
        if word in date_str.lower():
            return now.date() + timedelta(days=days)
    
    # Перевірка на дні тижня
    for weekday, day_num in WEEKDAYS.items():
        if weekday in date_str.lower():
            current_weekday = now.weekday()
            days_ahead = day_num - current_weekday
            if days_ahead <= 0:  # Якщо день вже минув цього тижня
                days_ahead += 7
            return now.date() + timedelta(days=days_ahead)
    
    return None

def parse_datetime(text: str) -> Optional[datetime]:
    """Парсить дату та час з тексту"""
    # Видаляємо зайві пробіли
    text = text.strip().lower()
    
    # Парсимо дату
    date = parse_date(text)
    if not date:
        return None
    
    # Парсимо час
    time = parse_time(text)
    if not time:
        # Якщо час не вказано, встановлюємо поточний час
        time = (datetime.now().hour, datetime.now().minute)
    
    # Об'єднуємо дату та час
    return datetime.combine(date, datetime.min.time().replace(hour=time[0], minute=time[1]))

def parse_reminder_text(text: str) -> Dict:
    """Парсить текст нагадування на пошук дати, часу та періодичності"""
    result = {
        "text": text,
        "remind_at": None,
        "repeat": None
    }
    
    # Шукаємо спеціальний формат date#DD.MM.YYYY time#HH:MM repeat#TYPE
    date_match = re.search(r"date#(\d{2}\.\d{2}\.\d{4})", text)
    time_match = re.search(r"time#(\d{2}:\d{2})", text)
    repeat_match = re.search(r"repeat#(\w+)", text)
    
    if date_match and time_match:
        try:
            date_str = date_match.group(1)
            time_str = time_match.group(1)
            day, month, year = map(int, date_str.split('.'))
            hours, minutes = map(int, time_str.split(':'))
            result["remind_at"] = datetime(year, month, day, hours, minutes)
        except ValueError:
            pass
    
    if repeat_match:
        repeat_type = repeat_match.group(1).lower()
        if repeat_type in [rt.value for rt in RepeatType]:
            result["repeat"] = RepeatType(repeat_type)
    
    # Якщо не знайдено спеціальний формат, шукаємо в природній мові
    if not result["remind_at"]:
        result["remind_at"] = parse_datetime(text)
    
    if not result["repeat"]:
        for keyword, repeat_type in REPEAT_KEYWORDS.items():
            if keyword in text.lower():
                result["repeat"] = repeat_type
                break
    
    # Видаляємо спеціальні маркери з тексту
    result["text"] = re.sub(r"date#\d{2}\.\d{2}\.\d{4}\s*", "", result["text"])
    result["text"] = re.sub(r"time#\d{2}:\d{2}\s*", "", result["text"])
    result["text"] = re.sub(r"repeat#\w+\s*", "", result["text"])
    result["text"] = result["text"].strip()
    
    return result 
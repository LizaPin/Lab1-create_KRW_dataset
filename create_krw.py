import requests
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)  # Создание папки 'data', если она не существует

def fetch_krw_exchange_rate(url: str, retries: int = 3, delay: float = 5.0):
    """
    Получает текущий курс корейской вонны (KRW) с повторными попытками.

    Аргументы:
        url (str): URL для получения данных.
        retries (int): Количество попыток повторного запроса при сбое.
        delay (float): Задержка в секундах между попытками.

    Возвращает:
        tuple: Курс корейской вонны, URL для следующего исторического запроса и дата данных.
               Возвращает (None, None, None), если запрос не удался.
    """
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            krw_rate = data["Valute"]["KRW"]["Value"]
            previous_url = data["PreviousURL"]
            date = data["Date"]
            return krw_rate, previous_url, date
        except requests.RequestException as e:
            print(f"Ошибка получения данных: {e}. Попытка {attempt + 1} из {retries}")
            time.sleep(delay)
    return None, None, None

def create_krw_dataset(days: int, max_retries: int = 3, time_delay: float = 0.7):
    """
    Собирает данные курса корейской вонны (KRW) за указанный период и сохраняет их в CSV-файл.
    
    Аргументы:
        days (int): Количество дней для сбора данных.
        max_retries (int): Максимальное количество попыток для получения данных.
        time_delay (float): Задержка в секундах между запросами.
    
    Возвращает:
        str: Имя созданного файла с данными.
    """
    filename = DATA_DIR / f"KRW_dataset_{int(time.time())}.csv"
    current_url = BASE_URL
    current_day = 1

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Дата;Курс KRW\n")
        while current_day <= days:
            krw_rate, next_url, date = fetch_krw_exchange_rate(current_url, max_retries)
            if krw_rate is None or next_url is None:
                print(f"Ошибка получения данных для дня #{current_day}, пропуск.")
                current_day += 1
                continue

            # Преобразование даты с помощью datetime
            date = datetime.strptime(date.split("T")[0], "%Y-%m-%d").date()
            file.write(f"{date};{krw_rate}\n")
            print(f"День #{current_day}. Дата: {date}. Курс KRW: {krw_rate}₽")

            current_url = "https:" + next_url
            current_day += 1
            time.sleep(time_delay)

    print(f"Датасет сохранён в файл {filename}")
    return str(filename)

def get_user_input(prompt: str, default_value, value_type, condition=lambda x: True):
    """
    Обрабатывает ввод пользователя с проверкой и поддержкой значения по умолчанию.
    
    Аргументы:
        prompt (str): Сообщение для пользователя.
        default_value: Значение по умолчанию, если пользователь не ввел данные.
        value_type: Ожидаемый тип данных.
        condition (callable): Функция для проверки корректности ввода.

    Возвращает:
        Значение, введенное пользователем, приведенное к нужному типу.
    """
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                return default_value
            value = value_type(user_input)
            if condition(value):
                return value
            else:
                print("Ввод не соответствует необходимым условиям.")
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите корректное значение.")

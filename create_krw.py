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

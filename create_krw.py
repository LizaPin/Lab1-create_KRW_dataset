import requests
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)  # Создание папки 'data', если она не существует

# Заготовка для функции получения курса (пока без логики повторных попыток)
def fetch_krw_exchange_rate(url: str):
    response = requests.get(url)
    data = response.json()
    krw_rate = data["Valute"]["KRW"]["Value"]
    return krw_rate

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")
URL_PROVIDER = os.getenv("URL_PROVIDER")
AI_MODEL = os.getenv("AI_MODEL")
MINI_APP_URL = os.getenv("MINI_APP_URL")
API_HHRU_URL = os.getenv("API_HHRU_URL")

# Проверка
if not BOT_TOKEN or not AI_API_KEY:
    exit("Ошибка: BOT_TOKEN или AI_API_KEY не найдены в .env файле!")

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import MINI_APP_URL


def get_main_kb(user_id: int):
    # Добавляем ID пользователя в параметры URL, чтобы Flask знал, чьи данные искать
    url_with_id = f"{MINI_APP_URL}?user_id={user_id}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать диагностику", callback_data="start_diag")],
        [InlineKeyboardButton(text="📱 Открыть Mini App", web_app=WebAppInfo(url=url_with_id))]
    ])


def get_age_kb():
    # Создаем кнопки от 16 до 22
    buttons = [InlineKeyboardButton(text=str(age), callback_data=f"age_{age}") for age in range(16, 23)]

    # Распределяем кнопки: по 4 в ряд для красоты
    keyboard = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_education_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Школа", callback_data="edu_school")],
        [InlineKeyboardButton(text="СПО", callback_data="edu_college")],
        [InlineKeyboardButton(text="ВУЗ", callback_data="edu_university")]
    ])
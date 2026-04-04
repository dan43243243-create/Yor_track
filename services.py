import aiohttp
from openai import AsyncOpenAI
from config import AI_API_KEY, AI_MODEL, URL_PROVIDER, API_HHRU_URL

ai_client = AsyncOpenAI(
    api_key=AI_API_KEY,
    base_url=URL_PROVIDER
)


async def get_career_track(data: dict):
    """
    Анализирует профиль, очищает данные (имя, город, з/п) и генерирует:
    Советы, План развития и Идеи для проектов.
    """
    try:
        # Системный промт с двойной задачей: очистка и генерация
        system_prompt = (
            "You are a professional career architect. Response strictly in RUSSIAN.\n"
            "Your task is twofold:\n"
            "1. Clean user data: Capitalize names (мишка -> Михаил), format salary (20тыс -> 20000), validate city.\n"
            "2. Generate career advice and plan.\n\n"
            "STRICT RULES:\n"
            "- [CLEAN_DATA] must be: Name | City | Salary (NUMBER ONLY, no currency symbols).\n"
            "- Each plan step and project MUST start with a dash (-).\n\n"
            "STRICT OUTPUT FORMAT:\n"
            "[CLEAN_DATA] Name | City | Salary\n"
            "[ADVICE] 3 sentences of career guidance.\n"
            "[PLAN]\n- Step 1\n- Step 2\n"
            "[PROJECTS]\n- Project 1\n- Project 2\n"
            "[QUERY] Short job title\n"
            "If input is nonsense, return ONLY: [INVALID_DATA]"
        )

        user_prompt = (
            f"Name: {data.get('name')}\n"
            f"City: {data.get('city')}\n"
            f"Salary: {data.get('salary')}\n"
            f"Education: {data.get('education')}\n"
            f"Interests: {data.get('interests')}\n"
            f"Skills: {data.get('skills')}"
        )

        response = await ai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        full_text = response.choices[0].message.content

        if "[INVALID_DATA]" in full_text:
            return None

        # Функция-помощник для вырезания текста между тегами
        def extract(tag, text):
            try:
                parts = text.split(f"[{tag}]")
                if len(parts) < 2: return ""
                # Берем контент до следующей открывающей скобки тега
                return parts[1].split("[")[0].strip()
            except:
                return ""

        # 1. Парсим очищенные данные
        clean_raw = extract("CLEAN_DATA", full_text)

        # Значения по умолчанию из исходных данных
        name = data.get('name', 'Гость')
        city = data.get('city', 'Не указан')
        salary = data.get('salary', '0')

        if "|" in clean_raw:
            parts = clean_raw.split("|")
            if len(parts) >= 3:
                name = parts[0].strip()
                city = parts[1].strip()
                # Оставляем только цифры в зарплате (удаляем 'руб', 'k', пробелы)
                salary_only_digits = "".join(filter(str.isdigit, parts[2].strip()))
                if salary_only_digits:
                    salary = salary_only_digits

        # 2. Формируем итоговый словарь результатов
        return {
            "name": name,
            "city": city,
            "salary": salary,
            "advice": extract("ADVICE", full_text),
            "plan": extract("PLAN", full_text),
            "projects": extract("PROJECTS", full_text),
            "query": extract("QUERY", full_text).replace("]", "").strip()
        }

    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return None


async def fetch_hh_vacancies(keyword: str) -> list:
    """Поиск вакансий на HeadHunter по ключевому слову"""
    if not keyword or len(keyword) < 2:
        return []

    params = {
        "text": keyword,
        "per_page": 5,
        "order_by": "publication_time"
    }
    headers = {"User-Agent": "MTS_Bot/1.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(API_HHRU_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {'title': i['name'], 'url': i['alternate_url']}
                        for i in data.get('items', [])
                    ]
                return []
        except Exception as e:
            print(f"Ошибка HH API: {e}")
            return []
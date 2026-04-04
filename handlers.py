from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import save_user_profile
from keyboards import get_main_kb, get_education_kb, get_age_kb
from services import get_career_track, fetch_hh_vacancies

router = Router()


class Diagnostic(StatesGroup):
    name = State()
    age = State()
    education = State()
    city = State()
    salary = State()
    interests = State()
    skills = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🚀 Привет! Я твой AI-наставник. Давай построим твой карьерный трек.",
        reply_markup=get_main_kb(message.from_user.id)
    )


@router.callback_query(F.data == "start_diag")
async def start_diagnostic(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Как тебя зовут?")
    await state.set_state(Diagnostic.name)
    await callback.answer()


@router.message(Diagnostic.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?", reply_markup=get_age_kb())
    await state.set_state(Diagnostic.age)


@router.callback_query(F.data.startswith("age_"))
async def process_age(callback: CallbackQuery, state: FSMContext):
    age = callback.data.split("_")[1]
    await state.update_data(age=age)
    await callback.message.answer("Где ты учишься?", reply_markup=get_education_kb())
    await state.set_state(Diagnostic.education)
    await callback.answer()


@router.callback_query(F.data.startswith("edu_"))
async def process_education(callback: CallbackQuery, state: FSMContext):
    edu_map = {"edu_school": "Школа", "edu_college": "СПО", "edu_university": "ВУЗ"}
    await state.update_data(education=edu_map.get(callback.data))
    await callback.message.answer("В каком городе ты хочешь работать?")
    await state.set_state(Diagnostic.city)
    await callback.answer()


@router.message(Diagnostic.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Какую зарплату ты ожидаешь (в месяц)?")
    await state.set_state(Diagnostic.salary)


@router.message(Diagnostic.salary)
async def process_salary(message: Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await message.answer("Расскажи о своих интересах?")
    await state.set_state(Diagnostic.interests)


@router.message(Diagnostic.interests)
async def process_interests(message: Message, state: FSMContext):
    await state.update_data(interests=message.text)
    await message.answer("Какие у тебя есть навыки?")
    await state.set_state(Diagnostic.skills)


@router.message(Diagnostic.skills)
async def process_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    user_input_data = await state.get_data()

    status_msg = await message.answer("🤖 ИИ проверяет данные и строит маршрут...")

    # 1. Получаем результат от ИИ
    ai_res = await get_career_track(user_input_data)

    await status_msg.delete()

    # Проверка на корректность (СБРОС НА НАЧАЛО ПРИ ОШИБКЕ)
    if not ai_res:
        await message.answer(
            "⚠️ Не удалось составить план. Пожалуйста, опиши данные подробнее."
        )
        # Полностью очищаем старые данные и переводим на ввод имени
        await state.clear()
        await state.set_state(Diagnostic.name)
        await message.answer("Давай попробуем еще раз. Как тебя зовут?")
        return

    # 2. Используем нормализованные данные от ИИ (ai_res)
    final_data = {
        'name': ai_res['name'],      # ИИ исправил регистр
        'age': user_input_data.get('age'),
        'education': user_input_data.get('education'),
        'city': ai_res['city'],      # ИИ нормализовал город
        'salary': ai_res['salary'],  # ИИ оставил только ЧИСЛО
        'interests': user_input_data.get('interests'),
        'skills': user_input_data.get('skills'),
        'role': ai_res['query'],
        'advice': ai_res['advice'],
        'plan': ai_res['plan'],
        'projects': ai_res['projects'],
        'score': 0  # Сброс прогресса для нового трека
    }

    # 3. Сохранение в бд
    save_user_profile(message.from_user.id, final_data)

    # 4. Ответ в телеграмм
    await message.answer(
        f"💡 <b>Твой карьерный вектор:</b> {final_data['role']}\n\n{ai_res['advice']}",
        parse_mode="HTML"
    )

    # 5. Поиск вакансий (используем очищенный запрос от ИИ)
    links = await fetch_hh_vacancies(ai_res['query'])
    if links:
        buttons = []
        for link in links[:5]:
            buttons.append([InlineKeyboardButton(text=link['title'], url=link['url'])])
        kb_links = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("🔍 Вот свежие вакансии по твоему направлению:", reply_markup=kb_links)
    else:
        await message.answer("🔍 Прямо сейчас вакансий не нашлось, но твой план развития уже ждет в приложении!")

    await state.clear()
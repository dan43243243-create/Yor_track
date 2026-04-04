import asyncio
import multiprocessing
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router
from database import init_db
from web_app import app

def run_flask():
    """Запуск Flask. Все настройки хоста и порта теперь только здесь."""
    print("🌐 Flask-сервер запущен на http://0.0.0.0:5000")
    # debug=False и use_reloader=False критически важны для multiprocessing!
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

async def run_bot():
    """Запуск асинхронного бота."""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("🤖 Бот запущен и готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # 1. Готовим общую базу данных для обоих процессов
    init_db()

    # 2. Создаем процесс для веба
    flask_process = multiprocessing.Process(target=run_flask)
    flask_process.start()

    # 3. Запускаем бота в главном процессе
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Остановка всех систем...")
        flask_process.terminate()
        flask_process.join()
        print("✅ Сервисы успешно остановлены.")
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Используем твою текущую версию базы
DB_PATH = os.path.join(BASE_DIR, 'users_ver.db')


def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Таблица пользователей
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS users
                           (
                               user_id
                               INTEGER
                               PRIMARY
                               KEY,
                               name
                               TEXT,
                               age
                               TEXT,
                               education
                               TEXT,
                               city
                               TEXT,
                               salary
                               TEXT,
                               interests
                               TEXT,
                               skills
                               TEXT,
                               score
                               INTEGER,
                               role
                               TEXT,
                               advice
                               TEXT,
                               plan
                               TEXT,
                               projects
                               TEXT
                           )
                           ''')

            # Таблица для хранения состояния галочек
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS user_progress
                           (
                               user_id
                               INTEGER,
                               task_id
                               TEXT,
                               is_completed
                               INTEGER,
                               PRIMARY
                               KEY
                           (
                               user_id,
                               task_id
                           )
                               )
                           ''')

            conn.commit()
            print(f"✅ База данных готова: {DB_PATH}")
    except Exception as e:
        print(f"❌ Ошибка БД при инициализации: {e}")


def save_user_profile(user_id, data):
    """
    Сохраняет новый профиль пользователя.
    Перед сохранением УДАЛЯЕТ старый прогресс (галочки),
    чтобы при перепрохождении трека всё сбросилось.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # 1. Очищаем старые галочки пользователя
            cursor.execute('DELETE FROM user_progress WHERE user_id = ?', (user_id,))

            # 2. Сохраняем новые данные профиля (план и проекты)
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, data.get('name'), data.get('age'), data.get('education'),
                data.get('city'), data.get('salary'), data.get('interests'),
                data.get('skills'), data.get('score', 85), data.get('role'),
                data.get('advice'), data.get('plan'), data.get('projects')
            ))

            conn.commit()
            print(f"✅ Профиль ID {user_id} обновлен, прогресс сброшен.")
    except Exception as e:
        print(f"❌ Ошибка сохранения профиля: {e}")


def get_user_profile(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"❌ Ошибка получения профиля: {e}")
        return None


def set_task_status(user_id, task_id, is_completed):
    """Обновляет статус конкретной задачи (выполнено/нет) в Mini App"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_progress (user_id, task_id, is_completed)
                VALUES (?, ?, ?)
            ''', (user_id, task_id, int(is_completed)))
            conn.commit()
    except Exception as e:
        print(f"❌ Ошибка сохранения статуса задачи: {e}")


def get_user_progress(user_id):
    """Возвращает словарь выполненных задач для загрузки в Mini App"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT task_id, is_completed FROM user_progress WHERE user_id = ?', (user_id,))
            return {row[0]: bool(row[1]) for row in cursor.fetchall()}
    except Exception as e:
        print(f"❌ Ошибка получения прогресса: {e}")
        return {}
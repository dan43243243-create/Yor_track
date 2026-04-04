from flask import Flask, render_template, request, jsonify
from database import get_user_profile, set_task_status, get_user_progress

app = Flask(__name__)


@app.route('/update_task', methods=['POST'])
def update_task():
    """Эндпоинт для сохранения состояния галочек в БД"""
    try:
        data = request.json
        user_id = data.get('user_id')
        task_id = data.get('task_id')
        is_completed = data.get('is_completed')

        if user_id and task_id is not None:
            set_task_status(user_id, task_id, is_completed)
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "Missing data"}), 400
    except Exception as e:
        print(f"Ошибка при обновлении задачи: {e}")
        return jsonify({"status": "error"}), 500


@app.route('/')
def index():
    # Телеграм передает данные через URL (например, ?user_id=12345)
    user_id = request.args.get('user_id')
    print(f"Запрос для ID: {user_id}")  # Для отладки в консоли

    profile = get_user_profile(user_id) if user_id else None
    # Получаем сохраненный прогресс (выполненные галочки)
    progress = get_user_progress(user_id) if user_id else {}

    # Если в базе нет пользователя, даем демо-данные
    if not profile:
        profile = {
            'user_id': user_id or 0,
            'name': 'Гость',
            'score': 0,
            'role': 'Не определено',
            'city': 'Не указан',
            'salary': '-',
            'skills': 'Нет данных',
            'plan': '',
            'projects': ''
        }

    return render_template('index.html', user=profile, progress=progress)


if __name__ == "__main__":
    # debug=True поможет видеть ошибки сразу в консоли при разработке
    app.run(host='0.0.0.0', port=5000, debug=True)
import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import calendar
from mood_utils import add_mood, get_month_moods
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler
import os

TOKEN = "7666621990:AAGxkqd-rMSjzMeEZgCLm_iPU__fBSFf_DE"
ADMIN_USER_IDS = {"870004624"}  # замените на свой Telegram user_id (число)

def start(update, context):
    keyboard = [
        [InlineKeyboardButton(
            "Открыть Календарь настроения",
            web_app=WebAppInfo(url="https://calendar-nr7j.onrender.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет! Нажми кнопку, чтобы открыть мини-приложение:', reply_markup=reply_markup)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

app = Flask(__name__)
DB_PATH = "database.db"

def calculate_mood_level(moods):
    if not moods:
        return 0
    moods_with_value = [e for e in moods.values() if e.get("mood") in ("happy", "neutral", "sad")]
    if not moods_with_value:
        return 0
    happy_count = sum(1 for e in moods_with_value if e.get("mood") == "happy")
    total = len(moods_with_value)
    level = (happy_count / total) * 100
    return round(level)

def get_all_time_stats(user_id):
    """
    Правильный подсчет настроений за все время:
    Учитываем по каждой дате только последнее состояние.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Получаем последние записи настроения для каждого дня
    cursor.execute("""
        SELECT date, mood FROM moods
        WHERE user_id = ? AND mood IN ('happy', 'neutral', 'sad')
        GROUP BY date
        HAVING MAX(id)
    """, (user_id,))
    rows = cursor.fetchall()

    # Альтернативный запрос, если выше не сработает (sqlite не поддерживает HAVING MAX(id) так просто):
    # Можно выбрать последние записи через подзапрос, например:

    cursor.execute("""
        SELECT m.date, m.mood FROM moods m
        INNER JOIN (
            SELECT date, MAX(id) as max_id FROM moods
            WHERE user_id = ? AND mood IN ('happy', 'neutral', 'sad')
            GROUP BY date
        ) sub ON m.id = sub.max_id
    """, (user_id,))
    rows = cursor.fetchall()

    conn.close()

    stats = {"happy": 0, "neutral": 0, "sad": 0, "total": 0}
    for mood_date, mood_val in rows:
        stats[mood_val] = stats.get(mood_val, 0) + 1
        stats["total"] += 1
    return stats

def get_all_time_comments(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, comment FROM moods
        WHERE user_id = ? AND comment IS NOT NULL AND TRIM(comment) != ''
        ORDER BY date ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return [{"date": row[0], "comment": row[1]} for row in rows]

@app.route('/')
def index():
    return render_template("calendar.html",
                           year=0,
                           month=0,
                           days=[],
                           moods={},
                           mood_level=0)

@app.route('/submit_mood', methods=['POST'])
def submit_mood():
    user_id = request.form.get("user_id", "default_user")
    date = request.form['date']
    mood = request.form['mood']
    comment = request.form.get('comment', '')

    # Обновляем запись, если есть, иначе создаём
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Проверяем, есть ли запись на эту дату
    cursor.execute("SELECT id FROM moods WHERE user_id = ? AND date = ?", (user_id, date))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE moods SET mood = ?, comment = ?
            WHERE id = ?
        """, (mood, comment, row[0]))
    else:
        cursor.execute("""
            INSERT INTO moods (user_id, date, mood, comment)
            VALUES (?, ?, ?, ?)
        """, (user_id, date, mood, comment))
    conn.commit()
    conn.close()

    return '', 200

@app.route('/get_mood_level')
def get_mood_level():
    user_id = request.args.get("user_id", "default_user")
    today = datetime.today()
    moods = get_month_moods(user_id, today.year, today.month)
    mood_level = calculate_mood_level(moods)
    return jsonify({"mood_level": mood_level})

@app.route('/clear_all_moods', methods=['POST'])
def clear_all_moods():
    user_id = request.form.get("user_id", "default_user")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM moods WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_comments')
def get_comments():
    user_id = request.args.get("user_id", "default_user")
    today = datetime.today()
    moods = get_month_moods(user_id, today.year, today.month)
    comments = []
    for date, entry in sorted(moods.items()):
        comment = entry.get('comment', '').strip()
        if comment:
            comments.append({"date": date, "comment": comment})
    return jsonify(comments)

@app.route('/get_calendar_data')
def get_calendar_data():
    user_id = request.args.get("user_id", "default_user")
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not year or not month:
        return jsonify({"error": "year и month обязательны"}), 400

    moods = get_month_moods(user_id, year, month)
    days_in_month = calendar.monthrange(year, month)[1]
    mood_level = calculate_mood_level(moods)

    days = []
    for day in range(1, days_in_month + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        entry = moods.get(date_str, {})
        days.append({
            "day": day,
            "date_str": date_str,
            "mood": entry.get("mood", ""),
            "comment": entry.get("comment", "")
        })

    comments = [{"date": date, "comment": data.get("comment","")} for date, data in moods.items() if data.get("comment","").strip()]

    all_time_stats = get_all_time_stats(user_id)
    all_time_comments = get_all_time_comments(user_id)

    return jsonify({
        "year": year,
        "month": month,
        "days": days,
        "mood_level": mood_level,
        "comments": comments,
        "all_time_stats": all_time_stats,
        "all_time_comments": all_time_comments
    })

@app.route('/admin/users')
def admin_users():
    from flask import request, jsonify
    import sqlite3

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search_user = request.args.get('search_user', '').strip()
        search_date = request.args.get('search_date', '').strip()
        requester_user_id = request.args.get('user_id', '')

        # Только admin (вписан вручную)
        requester_user_id = str(request.args.get('user_id', ''))
        if requester_user_id not in ADMIN_USER_IDS:
            return jsonify({'error': 'Доступ запрещён'}), 403

        conn = sqlite3.connect(DB_PATH)

        c = conn.cursor()

        base_query = "SELECT id, user_id, date, mood, comment FROM moods WHERE 1=1"
        params = []

        if search_user:
            base_query += " AND user_id LIKE ?"
            params.append(f"%{search_user}%")

        if search_date:
            base_query += " AND date = ?"
            params.append(search_date)

        count_query = f"SELECT COUNT(*) FROM ({base_query})"
        c.execute(count_query, params)
        total_count = c.fetchone()[0]

        base_query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params += [per_page, (page - 1) * per_page]

        c.execute(base_query, params)
        rows = c.fetchall()

        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'user_id': row[1],
                'date': row[2],
                'mood': row[3],
                'comment': row[4]
            })

        return jsonify({
            'data': data,
            'page': page,
            'per_page': per_page,
            'total_count': total_count
        })

    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

import sqlite3

DB_PATH = "database.db"

def add_mood(user_id, date, mood, comment=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO moods (user_id, date, mood, comment) VALUES (?, ?, ?, ?)
        """,
        (user_id, date, mood, comment)
    )
    conn.commit()
    conn.close()

def get_month_moods(user_id, year, month):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, mood, comment FROM moods
        WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
    """, (user_id, str(year), f"{month:02d}"))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {"mood": row[1], "comment": row[2]} for row in rows}

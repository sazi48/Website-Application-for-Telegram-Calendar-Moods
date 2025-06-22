# init_db.py
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    mood TEXT NOT NULL,
    comment TEXT,
    status TEXT NOT NULL DEFAULT 'active'
)
""")

conn.commit()
conn.close()

print("✅ Таблица 'moods' создана.")
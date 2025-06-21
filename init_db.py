import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    mood TEXT NOT NULL,
    comment TEXT,
    UNIQUE(user_id, date) ON CONFLICT REPLACE
)
""")

conn.commit()
conn.close()

print("✅ Таблица 'moods' создана или обновлена.")

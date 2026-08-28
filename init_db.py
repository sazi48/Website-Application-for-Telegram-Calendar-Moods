import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    mood TEXT NOT NULL DEFAULT '',   -- дефолт пустая строка
    comment TEXT NOT NULL DEFAULT '', -- дефолт пустая строка
    status TEXT NOT NULL DEFAULT 'active'
)
""")

conn.commit()
conn.close()

print("✅ Table 'moods' created.")

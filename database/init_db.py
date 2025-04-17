import sqlite3

conn = sqlite3.connect('uploads.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    email TEXT NOT NULL
)
''')

conn.commit()
conn.close()

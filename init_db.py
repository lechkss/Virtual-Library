# init_db.py
from app import get_db

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            reviews TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("База данных инициализирована!")

    conn = get_db()
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("База данных инициализирована!")

if __name__ == '__main__':
    init_db()
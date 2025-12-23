import sqlite3

def get_db():
    return sqlite3.connect("game.db")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        money INTEGER,
        military INTEGER,
        factories INTEGER
    )
    """)

    conn.commit()
    conn.close()

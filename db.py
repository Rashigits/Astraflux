import sqlite3
from contextlib import contextmanager

DB_PATH = "astraflux.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit() 
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_username TEXT,
            ip_address TEXT,
            login_time INTEGER
        )
    """)
    conn.commit()
    conn.close()

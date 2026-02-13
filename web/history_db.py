import sqlite3

DB_NAME = "history.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_history_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readiness_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            month TEXT,
            readiness_score INTEGER,
            readiness_level TEXT,
            financial_profile TEXT,
            key_risk TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_history_db()

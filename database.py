import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "tutor.db"
DB_PATH.parent.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Старая таблица истории
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    # Статистика
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            subject TEXT PRIMARY KEY,
            solved INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0
        )
    """)
    # НОВОЕ: сессии чата
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    # НОВОЕ: сообщения в сессиях
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    for subj in ("math", "physics", "chatbot"):
        cur.execute("INSERT OR IGNORE INTO stats (subject) VALUES (?)", (subj,))
    # Индексы для ускорения поиска
    cur.execute("CREATE INDEX IF NOT EXISTS idx_history_subject ON history(subject)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at)")
    conn.commit()
    conn.close()


# ─── Старые функции (не трогаем) ───

def save_interaction(subject: str, question: str, answer: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (subject, question, answer, timestamp) VALUES (?, ?, ?, ?)",
        (subject, question, answer, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def update_stats(subject: str, correct: bool):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO stats (subject) VALUES (?)", (subject,))
    cur.execute("UPDATE stats SET solved = solved + 1 WHERE subject = ?", (subject,))
    if correct:
        cur.execute("UPDATE stats SET correct = correct + 1 WHERE subject = ?", (subject,))
    conn.commit()
    conn.close()


def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT subject, solved, correct FROM stats")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_history(limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT subject, question, answer, timestamp FROM history ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def search_history(query: str, limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT subject, question, answer, timestamp FROM history "
        "WHERE question LIKE ? OR answer LIKE ? "
        "ORDER BY id DESC LIMIT ?",
        (f"%{query}%", f"%{query}%", limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# ─── НОВОЕ: работа с сессиями чата ───

def create_session(title: str = "Новый чат") -> int:
    """Создаёт новую сессию, возвращает её id."""
    now = datetime.now().isoformat(timespec="seconds")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_sessions (title, created_at, updated_at) VALUES (?, ?, ?)",
        (title, now, now),
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    return session_id


def add_message(session_id: int, role: str, content: str):
    """Добавляет сообщение в сессию. role: user или assistant."""
    now = datetime.now().isoformat(timespec="seconds")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, now),
    )
    cur.execute(
        "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
        (now, session_id),
    )
    conn.commit()
    conn.close()


def get_session_messages(session_id: int, limit: int = 20) -> list:
    """Возвращает последние N сообщений сессии. [{'role': ..., 'content': ...}]"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content, timestamp FROM chat_messages "
        "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    # Возвращаем в хронологическом порядке
    rows.reverse()
    return [{"role": r[0], "content": r[1]} for r in rows]


def list_sessions(limit: int = 20) -> list:
    """Список сессий: [(id, title, updated_at), ...]"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, updated_at FROM chat_sessions "
        "ORDER BY updated_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_session(session_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    cur.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

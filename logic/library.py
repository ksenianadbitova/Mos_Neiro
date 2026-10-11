"""
Библиотека документов: индексация папки + полнотекстовый поиск.
Использует sqlite3 FTS5 — встроенный в Python, не требует установки.
"""
import re
from pathlib import Path
from datetime import datetime
import sqlite3

from logic.document_reader import read_file


# Путь к отдельной БД библиотеки
LIB_DB = Path(__file__).parent.parent / "data" / "library.db"
LIB_DB.parent.mkdir(exist_ok=True)


def _connect():
    conn = sqlite3.connect(LIB_DB)
    # Включаем FTS5 и WAL для скорости
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_library():
    """Создаёт таблицы библиотеки."""
    conn = _connect()
    cur = conn.cursor()

    # Основная таблица документов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            total_chars INTEGER DEFAULT 0,
            total_pages INTEGER DEFAULT 0,
            indexed_at TEXT NOT NULL
        )
    """)

    # FTS5-таблица с текстом страниц
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(
            doc_id UNINDEXED,
            page_num UNINDEXED,
            text,
            tokenize='unicode61 remove_diacritics 2'
        )
    """)

    conn.commit()
    conn.close()


def _is_supported(path: Path) -> bool:
    return path.suffix.lower() in (".pdf", ".docx", ".txt", ".md")


def index_folder(folder: str, progress_cb=None) -> dict:
    """
    Индексирует все поддерживаемые файлы в папке.
    progress_cb(i, total, filename) — колбэк для отображения прогресса.
    Возвращает {'indexed': N, 'skipped': N, 'errors': [...]}.
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        return {"indexed": 0, "skipped": 0, "errors": [f"Папка не найдена: {folder}"]}

    init_library()

    # Собираем все файлы
    files = [p for p in folder_path.rglob("*") if p.is_file() and _is_supported(p)]

    total = len(files)
    indexed = 0
    skipped = 0
    errors = []

    conn = _connect()
    cur = conn.cursor()

    for i, f in enumerate(files):
        if progress_cb:
            try:
                progress_cb(i + 1, total, f.name)
            except Exception:
                pass

        # Проверяем, не индексирован ли уже
        cur.execute("SELECT id FROM documents WHERE path = ?", (str(f),))
        existing = cur.fetchone()

        try:
            mtime = f.stat().st_mtime
            # Если уже есть — сравним время изменения
            if existing:
                # Пропускаем — уже индексирован
                skipped += 1
                continue

            # Читаем файл
            result = read_file(str(f))
            if result.get("error"):
                errors.append(f"{f.name}: {result['error']}")
                continue

            # Добавляем документ
            cur.execute(
                "INSERT INTO documents (path, name, type, total_chars, total_pages, indexed_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (str(f), f.name, result["type"], result["total_chars"],
                 len(result["pages"]), datetime.now().isoformat(timespec="seconds"))
            )
            doc_id = cur.lastrowid

            # Добавляем страницы
            for pg in result["pages"]:
                text = pg.get("text", "").strip()
                if not text:
                    continue
                cur.execute(
                    "INSERT INTO pages (doc_id, page_num, text) VALUES (?, ?, ?)",
                    (doc_id, pg.get("page", 0), text)
                )

            indexed += 1

        except Exception as e:
            errors.append(f"{f.name}: {e}")

    conn.commit()
    conn.close()

    return {"indexed": indexed, "skipped": skipped, "errors": errors, "total": total}


def search_library(query: str, limit: int = 10) -> list:
    """
    Ищет в библиотеке через FTS5.
    Возвращает [{'doc': str, 'path': str, 'page': int, 'text': str, 'rank': float}, ...]
    """
    query = query.strip()
    if not query:
        return []

    # Простая санитизация: убираем спецсимволы FTS
    clean_q = re.sub(r"[^\w\sа-яёА-ЯЁ]", " ", query)
    clean_q = " ".join(clean_q.split())

    if not clean_q:
        return []

    init_library()
    conn = _connect()
    cur = conn.cursor()

    try:
        # FTS5 ищет фразы через OR по умолчанию
        cur.execute("""
            SELECT
                pages.text,
                pages.page_num,
                documents.name,
                documents.path,
                bm25(pages) AS rank
            FROM pages
            JOIN documents ON documents.id = pages.doc_id
            WHERE pages MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (clean_q, limit))
        rows = cur.fetchall()
    except Exception as e:
        conn.close()
        return [{"error": str(e)}]

    conn.close()

    results = []
    for text, page_num, name, path, rank in rows:
        # Обрезаем текст вокруг совпадения
        snippet = _extract_snippet(text, query, max_chars=400)
        results.append({
            "doc": name,
            "path": path,
            "page": page_num,
            "text": snippet,
            "rank": abs(rank),
        })
    return results


def _extract_snippet(text: str, query: str, max_chars: int = 400) -> str:
    """Ищет первое вхождение любого слова запроса и обрезает вокруг него."""
    if not text:
        return ""
    words = [w for w in re.findall(r"[а-яёa-z0-9]+", query.lower()) if len(w) >= 3]
    if not words:
        return text[:max_chars]

    low = text.lower()
    best_pos = -1
    for w in words:
        pos = low.find(w)
        if pos >= 0 and (best_pos < 0 or pos < best_pos):
            best_pos = pos

    if best_pos < 0:
        return text[:max_chars]

    # Берём 150 символов до и после
    start = max(0, best_pos - 150)
    end = min(len(text), best_pos + max_chars - 150)
    snippet = text[start:end]

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def list_indexed(limit: int = 100) -> list:
    """Возвращает список всех документов в индексе."""
    init_library()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, path, type, total_pages, indexed_at "
        "FROM documents ORDER BY indexed_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "path": r[2], "type": r[3],
         "pages": r[4], "indexed_at": r[5]}
        for r in rows
    ]


def clear_library():
    """Очищает всю библиотеку."""
    init_library()
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM pages")
    cur.execute("DELETE FROM documents")
    conn.commit()
    conn.close()


def library_stats() -> dict:
    """Статистика библиотеки."""
    init_library()
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM documents")
    docs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM pages")
    pages = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(total_chars), 0) FROM documents")
    chars = cur.fetchone()[0]
    conn.close()
    return {"docs": docs, "pages": pages, "chars": chars}

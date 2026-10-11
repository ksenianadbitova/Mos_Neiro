"""
Чтение PDF, DOCX и TXT.
Возвращает текст с разбивкой по страницам или абзацам.
"""
from pathlib import Path


def read_txt(path: str) -> str:
    """Читает текстовый файл."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"❌ Ошибка чтения TXT: {e}"


def read_docx(path: str) -> str:
    """Читает Word-документ."""
    try:
        from docx import Document
        doc = Document(path)
        parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text)
        return "\n".join(parts)
    except ImportError:
        return "❌ python-docx не установлен"
    except Exception as e:
        return f"❌ Ошибка чтения DOCX: {e}"


def read_pdf(path: str) -> list:
    """
    Читает PDF. Возвращает список страниц:
    [{'page': 1, 'text': '...'}, ...]
    """
    try:
        import fitz  # pymupdf
    except ImportError:
        return [{"page": 0, "text": "❌ pymupdf не установлен. Установи: python -m pip install pymupdf"}]

    pages = []
    try:
        doc = fitz.open(path)
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                pages.append({"page": i + 1, "text": text})
        doc.close()
    except Exception as e:
        pages.append({"page": 0, "text": f"❌ Ошибка чтения PDF: {e}"})

    return pages


def read_file(path: str) -> dict:
    """
    Универсальное чтение файла.
    Возвращает {'type': 'txt'|'docx'|'pdf', 'pages': [{'page': N, 'text': '...'}], 'total_chars': int}.
    """
    p = Path(path)
    if not p.exists():
        return {"type": "error", "pages": [], "total_chars": 0,
                "error": "Файл не найден"}

    ext = p.suffix.lower()

    if ext == ".txt" or ext == ".md":
        text = read_txt(path)
        return {
            "type": "txt",
            "pages": [{"page": 1, "text": text}],
            "total_chars": len(text),
            "error": None,
        }

    elif ext == ".docx":
        text = read_docx(path)
        return {
            "type": "docx",
            "pages": [{"page": 1, "text": text}],
            "total_chars": len(text),
            "error": None,
        }

    elif ext == ".pdf":
        pages = read_pdf(path)
        total = sum(len(pg["text"]) for pg in pages)
        return {
            "type": "pdf",
            "pages": pages,
            "total_chars": total,
            "error": None if pages else "PDF пустой или не читается",
        }

    else:
        return {"type": "unknown", "pages": [], "total_chars": 0,
                "error": f"Формат {ext} не поддерживается"}


def search_in_document(path: str, query: str, context_chars: int = 300) -> list:
    """
    Ищет запрос в документе.
    Возвращает список найденных фрагментов: [{'page': N, 'text': '...', 'score': X}].
    """
    import re

    result = read_file(path)
    if result.get("error"):
        return []

    # Токенизация запроса
    query_words = set(re.findall(r"[а-яёa-z]+", query.lower()))
    query_words = {w for w in query_words if len(w) >= 3}

    if not query_words:
        return []

    found = []
    for page_info in result["pages"]:
        page_num = page_info["page"]
        text = page_info["text"]

        # Разбиваем текст на абзацы
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

        for para in paragraphs:
            para_lower = para.lower()
            para_words = set(re.findall(r"[а-яёa-z]+", para_lower))
            para_words = {w for w in para_words if len(w) >= 3}

            # Считаем совпадения
            overlap = len(query_words & para_words)
            if overlap == 0:
                continue

            score = overlap / len(query_words)
            if score < 0.3:
                continue

            # Обрезаем до контекста
            fragment = para[:context_chars]
            if len(para) > context_chars:
                fragment += "..."

            found.append({
                "page": page_num,
                "text": fragment,
                "score": score,
            })

    # Сортируем по убыванию релевантности
    found.sort(key=lambda x: x["score"], reverse=True)
    return found[:5]


def get_summary(path: str, max_chars: int = 500) -> str:
    """Краткое описание документа: тип, количество страниц, начало."""
    result = read_file(path)
    if result.get("error"):
        return f"❌ {result['error']}"

    t = result["type"]
    pages = len(result["pages"])
    chars = result["total_chars"]

    lines = [
        f"📄 Файл: {Path(path).name}",
        f"📋 Тип: {t.upper()}",
        f"📑 Страниц: {pages}",
        f"📝 Символов: {chars}",
        "",
        "📖 Начало текста:",
        "",
    ]

    if result["pages"]:
        first = result["pages"][0]["text"][:max_chars]
        lines.append(first)
        if len(result["pages"][0]["text"]) > max_chars:
            lines.append("...")

    return "\n".join(lines)

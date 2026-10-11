"""
Поиск по локальной базе знаний (knowledge/).
Очень строгий — используется только при точных совпадениях.
"""
import re
from pathlib import Path
from collections import Counter


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а",
    "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же",
    "вы", "за", "бы", "по", "только", "ее", "мне", "было", "вот", "от",
    "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже",
    "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть", "был",
    "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там",
    "потом", "себя", "ничего", "ей", "может", "они", "тут", "где",
    "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была",
    "сам", "чтоб", "без", "будто", "чего", "раз", "тоже", "себе", "под",
    "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого",
    "какой", "совсем", "ним", "здесь", "этом", "один", "почти",
    "мой", "тем", "чтобы", "нее", "были", "куда", "зачем", "всех",
    "никогда", "можно", "при", "наконец", "два", "об", "другой", "хоть",
    "после", "над", "больше", "тот", "через", "эти", "нас", "про",
    "всего", "них", "какая", "много", "разве", "три", "эту", "моя",
    "это", "эта",
}

MIN_WORD_LEN = 3


def _tokenize(text: str) -> list:
    text = text.lower()
    words = re.findall(r"[а-яёa-z]+", text)
    return [w for w in words if len(w) >= MIN_WORD_LEN and w not in STOPWORDS]


def _load_documents() -> list:
    docs = []
    if not KNOWLEDGE_DIR.exists():
        return docs
    for path in KNOWLEDGE_DIR.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in (".txt", ".md"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        docs.append({
            "path": str(path.relative_to(KNOWLEDGE_DIR)),
            "title": path.stem.replace("_", " ").title(),
            "text": text,
            "words": Counter(_tokenize(text)),
        })
    return docs


_CACHE = None


def _get_docs():
    global _CACHE
    if _CACHE is None:
        _CACHE = _load_documents()
    return _CACHE


def reload():
    global _CACHE
    _CACHE = None


def stats() -> str:
    docs = _get_docs()
    if not docs:
        return "📭 База знаний пуста."
    lines = [f"📚 Файлов в базе: {len(docs)}\n"]
    for d in docs:
        lines.append(f"• {d['path']} ({len(d['text'])} симв.)")
    return "\n".join(lines)


def search(query: str, top_k: int = 3, min_score: float = 0.2) -> list:
    """Общий поиск — для справки, используется редко."""
    docs = _get_docs()
    if not docs:
        return []
    q_words = _tokenize(query)
    if not q_words:
        return []
    results = []
    for d in docs:
        score = sum(d["words"].get(w, 0) for w in q_words)
        total = sum(d["words"].values())
        if total == 0:
            continue
        score_norm = score / (total ** 0.5)
        if score_norm > min_score:
            results.append((score_norm, d))
    results.sort(reverse=True, key=lambda x: x[0])
    return [d for _, d in results[:top_k]]


def extract_relevant(query: str, text: str, max_chars: int = 800) -> str:
    q_words = set(_tokenize(query))
    if not q_words:
        return text[:max_chars]
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return text[:max_chars]
    scored = []
    for i, p in enumerate(paragraphs):
        words = set(_tokenize(p))
        overlap = len(q_words & words)
        scored.append((overlap, i, p))
    scored.sort(reverse=True, key=lambda x: x[0])
    top = [p for _, _, p in scored[:3]]
    result = "\n\n".join(top)
    if len(result) > max_chars:
        result = result[:max_chars].rsplit(" ", 1)[0] + "..."
    return result


def answer_from_kb(query: str, min_score: float = 0.75) -> str:
    """
    ОЧЕНЬ строгая проверка: используем базу только если
    ВСЕ значимые слова запроса есть в заголовке файла
    ИЛИ в тексте файла их не менее 80%.
    """
    docs = _get_docs()
    if not docs:
        return ""

    q_words = set(_tokenize(query))
    if len(q_words) < 1:
        return ""

    best_score = 0
    best_doc = None

    for d in docs:
        title_words = set(_tokenize(d["title"]))
        text_words = set(d["words"].keys())

        # Сколько значимых слов запроса в заголовке
        title_hits = len(q_words & title_words) / len(q_words)
        # Сколько значимых слов запроса в тексте
        text_hits = len(q_words & text_words) / len(q_words)

        # Заголовок важнее в 2 раза
        score = max(title_hits * 1.0, text_hits * 0.5)

        if score > best_score:
            best_score = score
            best_doc = d

    # Жёсткий порог: 75% слов запроса должны найтись
    if best_score < min_score or best_doc is None:
        return ""

    fragment = extract_relevant(query, best_doc["text"])
    return f"📚 Из базы знаний ({best_doc['title']}):\n{fragment}"

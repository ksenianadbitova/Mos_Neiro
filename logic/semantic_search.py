"""
Семантический поиск: ищет по смыслу, а не по словам.
Использует sentence-transformers (эмбеддинги) + ChromaDB (хранилище).
"""
from pathlib import Path
import hashlib
import re

try:
    from sentence_transformers import SentenceTransformer
    ST_OK = True
except ImportError:
    ST_OK = False

try:
    import chromadb
    CHROMA_OK = True
except ImportError:
    CHROMA_OK = False

from logic.document_reader import read_file


# Папка для векторной БД
VECTOR_DB_DIR = Path(__file__).parent.parent / "data" / "vector_db"
VECTOR_DB_DIR.mkdir(exist_ok=True)

# Имя модели - многоязычная, работает с русским
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Кэш модели в памяти
_MODEL = None
_CLIENT = None
_COLLECTION = None


def _get_model():
    """Ленивая загрузка модели (первый запуск - скачивание ~120 МБ)."""
    global _MODEL
    if _MODEL is None:
        if not ST_OK:
            return None
        try:
            _MODEL = SentenceTransformer(MODEL_NAME)
        except Exception:
            _MODEL = None
    return _MODEL


def _get_collection():
    """Ленивое подключение к ChromaDB."""
    global _CLIENT, _COLLECTION
    if _COLLECTION is None:
        if not CHROMA_OK:
            return None
        try:
            _CLIENT = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
            _COLLECTION = _CLIENT.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            return None
    return _COLLECTION


def is_available() -> bool:
    """Проверяет, доступен ли семантический поиск."""
    return ST_OK and CHROMA_OK


def _split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    """
    Разбивает текст на чанки по ~500 символов с перекрытием.
    Режем по границам предложений, чтобы не рвать смысл.
    """
    if not text or len(text) < 50:
        return []

    # Разбиваем на предложения
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) + 1 <= chunk_size:
            current = (current + " " + sent).strip() if current else sent
        else:
            if current:
                chunks.append(current)
            current = sent

    if current and len(current) > 30:
        chunks.append(current)

    return chunks


def index_document(path: str, progress_cb=None) -> dict:
    """
    Индексирует один документ: разбивает на чанки, создаёт вектора, сохраняет в ChromaDB.
    Возвращает {'chunks': N, 'error': str | None}.
    """
    if not is_available():
        return {"chunks": 0, "error": "sentence-transformers или chromadb не установлены"}

    model = _get_model()
    collection = _get_collection()
    if model is None or collection is None:
        return {"chunks": 0, "error": "Не удалось загрузить модель или БД"}

    p = Path(path)
    if not p.exists():
        return {"chunks": 0, "error": "Файл не найден"}

    # Проверяем, не проиндексирован ли уже
    doc_id = hashlib.md5(str(p).encode()).hexdigest()[:16]
    try:
        existing = collection.get(where={"doc_id": doc_id}, limit=1)
        if existing and existing.get("ids"):
            return {"chunks": 0, "error": None, "already_indexed": True}
    except Exception:
        pass

    # Читаем файл
    result = read_file(path)
    if result.get("error"):
        return {"chunks": 0, "error": result["error"]}

    # Собираем весь текст с указанием страниц
    all_chunks = []
    for page_info in result["pages"]:
        page_num = page_info.get("page", 1)
        text = page_info.get("text", "")
        chunks = _split_into_chunks(text)
        for ch in chunks:
            all_chunks.append({"text": ch, "page": page_num})

    if not all_chunks:
        return {"chunks": 0, "error": None, "empty": True}

    # Создаём эмбеддинги
    try:
        texts = [c["text"] for c in all_chunks]
        embeddings = model.encode(texts, show_progress_bar=False, batch_size=32)
    except Exception as e:
        return {"chunks": 0, "error": f"Ошибка эмбеддингов: {e}"}

    # Сохраняем в ChromaDB
    ids = [f"{doc_id}_{i}" for i in range(len(all_chunks))]
    metadatas = [
        {
            "doc_id": doc_id,
            "doc_name": p.name,
            "doc_path": str(p),
            "page": c["page"],
        }
        for c in all_chunks
    ]
    documents = [c["text"] for c in all_chunks]

    try:
        collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=documents,
        )
    except Exception as e:
        return {"chunks": 0, "error": f"Ошибка ChromaDB: {e}"}

    return {"chunks": len(all_chunks), "error": None}


def index_folder_semantic(folder: str, progress_cb=None) -> dict:
    """
    Семантически индексирует все документы в папке.
    progress_cb(i, total, name) - колбэк прогресса.
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        return {"indexed": 0, "chunks": 0, "errors": [f"Папка не найдена: {folder}"]}

    files = [p for p in folder_path.rglob("*")
             if p.is_file() and p.suffix.lower() in (".pdf", ".docx", ".txt", ".md")]

    total = len(files)
    indexed = 0
    total_chunks = 0
    errors = []

    for i, f in enumerate(files):
        if progress_cb:
            try:
                progress_cb(i + 1, total, f.name)
            except Exception:
                pass

        try:
            res = index_document(str(f))
            if res.get("error"):
                errors.append(f"{f.name}: {res['error']}")
            elif res.get("already_indexed"):
                pass  # Пропускаем
            else:
                indexed += 1
                total_chunks += res.get("chunks", 0)
        except Exception as e:
            errors.append(f"{f.name}: {e}")

    return {
        "indexed": indexed,
        "chunks": total_chunks,
        "errors": errors,
        "total": total,
    }


def search_semantic(query: str, top_k: int = 10) -> list:
    """
    Ищет ближайшие по смыслу фрагменты.
    Возвращает [{'doc': str, 'page': int, 'text': str, 'score': float}, ...].
    """
    if not is_available():
        return []

    model = _get_model()
    collection = _get_collection()
    if model is None or collection is None:
        return []

    try:
        query_embedding = model.encode([query], show_progress_bar=False)[0]
    except Exception:
        return []

    try:
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )
    except Exception:
        return []

    if not results or not results.get("ids") or not results["ids"][0]:
        return []

    found = []
    for i, doc_text in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i] if results.get("metadatas") else {}
        distance = results["distances"][0][i] if results.get("distances") else 1.0
        # ChromaDB с cosine: distance 0 = идеально, 1 = совершенно непохоже
        score = max(0.0, 1.0 - distance)
        found.append({
            "doc": meta.get("doc_name", "?"),
            "path": meta.get("doc_path", ""),
            "page": meta.get("page", 0),
            "text": doc_text[:500],
            "score": round(score, 3),
        })

    return found


def semantic_stats() -> dict:
    """Статистика векторной БД."""
    if not is_available():
        return {"docs": 0, "chunks": 0, "available": False}
    collection = _get_collection()
    if collection is None:
        return {"docs": 0, "chunks": 0, "available": False}
    try:
        count = collection.count()
        return {"chunks": count, "available": True}
    except Exception:
        return {"chunks": 0, "available": False}


def clear_semantic():
    """Очищает векторную БД."""
    if not is_available():
        return
    global _CLIENT, _COLLECTION
    try:
        if _CLIENT is not None:
            _CLIENT.delete_collection("documents")
            _COLLECTION = None
    except Exception:
        pass

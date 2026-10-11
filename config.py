"""
Центральный конфиг МосНейро.
Проверка библиотек, путей, окружения.
"""
import sys
from pathlib import Path


# ─── Пути ───
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
MODELS_DIR = PROJECT_ROOT / "models"

for p in (DATA_DIR, OUTPUT_DIR, KNOWLEDGE_DIR, MODELS_DIR):
    p.mkdir(exist_ok=True)


# ─── Библиотеки и их функции ───
REQUIRED_LIBS = {
    "customtkinter": "Интерфейс приложения",
    "PIL": "Работа с изображениями",
    "sympy": "Математические вычисления",
    "matplotlib": "Графики (опционально)",
    "wikipediaapi": "Поиск в Википедии",
    "requests": "HTTP-запросы",
    "bs4": "Разбор HTML",
    "docx": "Генерация документов Word",
    "ddgs": "Поиск в интернете",
    "deep_translator": "Перевод текста",
    "rapidocr_onnxruntime": "Распознавание текста с картинок",
}

OPTIONAL_LIBS = {
    "pymupdf": "Чтение PDF (необязательно)",
    "sentence_transformers": "Поиск по смыслу (необязательно)",
    "llama_cpp": "Локальная нейросеть (необязательно)",
}


def check_libs() -> dict:
    """Проверяет наличие библиотек. Возвращает {'ok': [], 'missing': []}."""
    ok = []
    missing = []
    for lib, desc in REQUIRED_LIBS.items():
        try:
            __import__(lib)
            ok.append((lib, desc))
        except ImportError:
            missing.append((lib, desc))
    return {"ok": ok, "missing": missing}


def check_optional() -> list:
    """Проверяет опциональные библиотеки. Возвращает [(lib, desc, ok)]."""
    result = []
    for lib, desc in OPTIONAL_LIBS.items():
        try:
            __import__(lib)
            result.append((lib, desc, True))
        except ImportError:
            result.append((lib, desc, False))
    return result


def get_status() -> str:
    """Возвращает статус окружения в виде текста."""
    lines = ["🧠 МосНейро — статус окружения", ""]

    lines.append(f"Python: {sys.version.split()[0]}")
    lines.append(f"Путь: {sys.executable}")
    lines.append("")

    lines.append("📁 Папки:")
    for name, p in [("data", DATA_DIR), ("output", OUTPUT_DIR),
                    ("knowledge", KNOWLEDGE_DIR), ("models", MODELS_DIR)]:
        exists = "✅" if p.exists() else "❌"
        lines.append(f"  {exists} {name}: {p}")

    lines.append("")
    lines.append("📦 Обязательные библиотеки:")
    libs = check_libs()
    for lib, desc in libs["ok"]:
        lines.append(f"  ✅ {lib} — {desc}")
    for lib, desc in libs["missing"]:
        lines.append(f"  ❌ {lib} — {desc}")

    lines.append("")
    lines.append("🎁 Опциональные библиотеки:")
    for lib, desc, ok in check_optional():
        icon = "✅" if ok else "⭕"
        lines.append(f"  {icon} {lib} — {desc}")

    lines.append("")
    if libs["missing"]:
        lines.append("⚠️ Некоторые обязательные библиотеки не установлены.")
        lines.append("Установи их командой:")
        libs_str = " ".join(m[0] for m in libs["missing"])
        lines.append(f"python -m pip install {libs_str}")
    else:
        lines.append("✅ Все обязательные библиотеки на месте!")

    return "\n".join(lines)

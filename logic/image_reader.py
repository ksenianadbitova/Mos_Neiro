"""Распознавание текста с картинок через rapidocr (ленивая загрузка)."""
from pathlib import Path

try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

# НЕ загружаем модель сразу — только при первом использовании
_ocr_engine = None
_ocr_loaded = False


def _get_ocr():
    """Ленивая инициализация OCR-движка."""
    global _ocr_engine, _ocr_loaded
    if _ocr_loaded:
        return _ocr_engine

    try:
        from rapidocr_onnxruntime import RapidOCR
        _ocr_engine = RapidOCR()
        _ocr_loaded = True
        return _ocr_engine
    except Exception:
        _ocr_loaded = True
        _ocr_engine = None
        return None


def extract_text(path: str) -> str:
    ocr = _get_ocr()
    if ocr is None:
        return ""
    try:
        result, _ = ocr(str(path))
        if not result:
            return ""
        lines = [item[1] for item in result if len(item) >= 2]
        return "\n".join(lines).strip()
    except Exception:
        return ""


def analyze_image(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"text": "", "filename": p.name, "error": "Файл не найден"}

    ocr = _get_ocr()
    if ocr is None:
        return {"text": "", "filename": p.name,
                "error": "OCR не установлен. Установи: python -m pip install rapidocr-onnxruntime"}

    text = extract_text(path)
    return {"text": text, "filename": p.name, "error": None}

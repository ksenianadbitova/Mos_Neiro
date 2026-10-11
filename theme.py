"""
Тема МосНейро: современная минималистичная палитра.
Один акцент, много воздуха, мягкие тени.
"""
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "theme_config.txt"


def _load_saved_mode():
    try:
        if CONFIG_FILE.exists():
            m = CONFIG_FILE.read_text(encoding="utf-8").strip()
            if m in ("dark", "light"):
                return m
    except Exception:
        pass
    return "light"


_CURRENT_MODE = _load_saved_mode()


# ═══════════════════════════════════════════
# СВЕТЛАЯ ТЕМА (по умолчанию)
# ═══════════════════════════════════════════
LIGHT = {
    # Фон
    "BG_DARK": "#F7F8FA",              # мягкий серо-белый (общий фон)
    "BG_CARD": "#FFFFFF",              # чистый белый (карточки)
    "BG_CARD_HOVER": "#F0F2F5",        # hover
    "BG_SIDEBAR": "#FFFFFF",           # белый sidebar
    "BG_INPUT": "#F0F2F5",             # поля ввода

    # Акцент — фиолетово-синий (как у Notion/Linear)
    "ACCENT": "#5B5BD6",
    "ACCENT_HOVER": "#4A4AC4",
    "ACCENT_LIGHT": "#EEEEFB",

    # Текст
    "TEXT_PRIMARY": "#1A1D28",
    "TEXT_SECONDARY": "#5A6175",
    "TEXT_MUTED": "#9CA3B0",
    "TEXT_INVERSE": "#FFFFFF",

    # Статусы
    "SUCCESS": "#10B981",
    "WARNING": "#F59E0B",
    "ERROR": "#EF4444",
    "INFO": "#3B82F6",

    # Границы
    "BORDER": "#E5E7EB",
    "BORDER_STRONG": "#D1D5DB",

    # Тени (через серый)
    "SHADOW": "#00000010",
}

# ═══════════════════════════════════════════
# ТЁМНАЯ ТЕМА
# ═══════════════════════════════════════════
DARK = {
    "BG_DARK": "#0E0E10",
    "BG_CARD": "#18181B",
    "BG_CARD_HOVER": "#232328",
    "BG_SIDEBAR": "#131316",
    "BG_INPUT": "#1F1F24",

    "ACCENT": "#7C7CFF",
    "ACCENT_HOVER": "#6868E5",
    "ACCENT_LIGHT": "#25254D",

    "TEXT_PRIMARY": "#F5F5F7",
    "TEXT_SECONDARY": "#A1A1A8",
    "TEXT_MUTED": "#6B6B73",
    "TEXT_INVERSE": "#0E0E10",

    "SUCCESS": "#34D399",
    "WARNING": "#FBBF24",
    "ERROR": "#F87171",
    "INFO": "#60A5FA",

    "BORDER": "#2A2A30",
    "BORDER_STRONG": "#3A3A42",

    "SHADOW": "#00000040",
}


def get_colors() -> dict:
    return LIGHT if _CURRENT_MODE == "light" else DARK


def current_mode() -> str:
    return _CURRENT_MODE


def set_mode(mode: str):
    global _CURRENT_MODE
    if mode in ("dark", "light"):
        _CURRENT_MODE = mode
        try:
            CONFIG_FILE.write_text(mode, encoding="utf-8")
        except Exception:
            pass


# ─── Модульные переменные (для `from theme import ACCENT`) ───
_c = get_colors()
ACCENT = _c["ACCENT"]
ACCENT_HOVER = _c["ACCENT_HOVER"]
ACCENT_LIGHT = _c["ACCENT_LIGHT"]
BG_DARK = _c["BG_DARK"]
BG_CARD = _c["BG_CARD"]
BG_CARD_HOVER = _c["BG_CARD_HOVER"]
BG_SIDEBAR = _c["BG_SIDEBAR"]
BG_INPUT = _c["BG_INPUT"]
TEXT_PRIMARY = _c["TEXT_PRIMARY"]
TEXT_SECONDARY = _c["TEXT_SECONDARY"]
TEXT_MUTED = _c["TEXT_MUTED"]
TEXT_INVERSE = _c["TEXT_INVERSE"]
SUCCESS = _c["SUCCESS"]
WARNING = _c["WARNING"]
ERROR = _c["ERROR"]
INFO = _c["INFO"]
BORDER = _c["BORDER"]
BORDER_STRONG = _c["BORDER_STRONG"]

# Цвета разделов (мягкие, но выразительные)
MATH_COLOR = "#5B5BD6"       # фиолетово-синий
PHYSICS_COLOR = "#F97316"    # оранжевый
CHATBOT_COLOR = "#3B82F6"    # синий
WEB_COLOR = "#06B6D4"        # бирюзовый
GOST_COLOR = "#8B5CF6"       # фиолетовый
DOCS_COLOR = "#10B981"       # зелёный
LIBRARY_COLOR = "#EC4899"    # розовый
SETTINGS_COLOR = "#6B7280"   # серый
ENGLISH_COLOR = "#10B981"
STATS_COLOR = "#8B5CF6"

# Шрифты
FONT_FAMILY = "Segoe UI Variable"  # современный системный шрифт Windows 11
FONT_FAMILY_ALT = "Segoe UI"       # fallback

# Шкала размеров (для консистентности)
FONT_TINY = (FONT_FAMILY, 10)
FONT_SMALL = (FONT_FAMILY, 11)
FONT_BODY = (FONT_FAMILY, 13)
FONT_BODY_LG = (FONT_FAMILY, 14)
FONT_HEADING = (FONT_FAMILY, 16, "bold")
FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_DISPLAY = (FONT_FAMILY, 32, "bold")

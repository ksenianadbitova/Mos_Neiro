"""
Помощник по ГОСТ-документам.
- generate_title_page(data) — титульный лист
- generate_report(topic, data) — отчёт по теме
Оба открывают диалог сохранения файла.
"""
import re
from datetime import datetime
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Папка по умолчанию (если пользователь отменит диалог)
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════
# СОХРАНЕНИЕ ЧЕРЕЗ ДИАЛОГ
# ═══════════════════════════════════════════════════════

def _save_with_dialog(doc, default_name: str) -> str:
    """Открывает диалог сохранения файла и сохраняет туда документ."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filepath = filedialog.asksaveasfilename(
        title="Куда сохранить документ?",
        defaultextension=".docx",
        initialfile=default_name,
        initialdir=str(Path.home() / "Documents"),
        filetypes=[("Документ Word", "*.docx"), ("Все файлы", "*.*")],
    )
    root.destroy()

    if not filepath:
        # Пользователь отменил — сохраняем в output/
        filepath = OUTPUT_DIR / default_name
        doc.save(filepath)
        return f"⚠️ Диалог отменён. Сохранено по умолчанию:\n{filepath}"

    doc.save(filepath)
    return f"✅ Сохранено:\n{filepath}"


# ═══════════════════════════════════════════════════════
# ОБЩИЕ НАСТРОЙКИ ДОКУМЕНТА
# ═══════════════════════════════════════════════════════

def _setup_doc():
    """Создаёт документ с настройками по ГОСТ 7.32-2017."""
    doc = Document()
    for section in doc.sections:
        section.left_margin = Cm(3)
        section.right_margin = Cm(1.5)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(14)
    return doc


def _center(doc, text, bold=False, size=14, space_after=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Times New Roman"
    p.paragraph_format.space_after = Pt(space_after)
    return p


def _heading(doc, text, size=14):
    p = doc.add_paragraph()
    r = p.add_run(text.upper())
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(size)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    return p


def _subheading(doc, text, size=14):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(size)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    return p


def _body(doc, text):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.line_spacing = 1.5
    return p


# ═══════════════════════════════════════════════════════
# СПРАВКА
# ═══════════════════════════════════════════════════════

GOST_RULES = {
    "Шрифт": "Times New Roman, 14 пт (основной), 12 пт (сноски)",
    "Интервал": "Полуторный (1.5)",
    "Поля": "Левое 30 мм, правое 15 мм, верхнее и нижнее 20 мм",
    "Абзац": "Отступ 1.25 см, выравнивание по ширине",
    "Нумерация": "Страницы — снизу по центру (титульный не нумеруется)",
    "Заголовки": "Полужирные, без точки в конце",
    "Таблицы": "Подпись «Таблица N — Название» над таблицей",
    "Рисунки": "Подпись «Рисунок N — Название» под рисунком по центру",
    "Формулы": "По центру, номер в круглых скобках справа",
    "Ссылки": "В квадратных скобках [1, с. 25]",
    "Литература": "В алфавитном порядке, нумерованный список",
}


def get_rules() -> str:
    lines = ["📐 Правила оформления по ГОСТ 7.32-2017:\n"]
    for key, value in GOST_RULES.items():
        lines.append(f"• {key}: {value}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# ТИТУЛЬНЫЙ ЛИСТ
# ═══════════════════════════════════════════════════════

def generate_title_page(
    university: str = "Министерство науки и высшего образования РФ",
    faculty: str = "",
    department: str = "Кафедра информатики",
    doc_type: str = "ОТЧЁТ",
    subject: str = "Информатика",
    topic: str = "Тема работы",
    student: str = "Иванов И.И.",
    group: str = "ИС-21",
    teacher: str = "Петров П.П.",
    city: str = "Москва",
    year: int = None,
    **kwargs,
) -> str:
    """Создаёт титульный лист и открывает диалог сохранения."""
    if not DOCX_AVAILABLE:
        return "❌ Установи python-docx: python -m pip install python-docx"

    if year is None:
        year = datetime.now().year

    doc = _setup_doc()

    # Шапка
    _center(doc, university, size=12)
    if faculty:
        _center(doc, faculty, size=12)
    _center(doc, department, size=12)
    _center(doc, "")

    # Отступ
    for _ in range(6):
        _center(doc, "")

    # Тип работы
    _center(doc, doc_type, bold=True, size=16)
    _center(doc, f"по дисциплине «{subject}»", size=14)
    _center(doc, f"на тему: «{topic}»", size=14)

    # Отступ
    for _ in range(6):
        _center(doc, "")

    # Правый блок
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(f"Выполнил: студент группы {group}\n{student}\n\n")
    p.add_run(f"Проверил:\n{teacher}")

    # Отступ
    for _ in range(6):
        _center(doc, "")

    _center(doc, f"{city}, {year}")

    filename = f"Титульный_лист_{datetime.now():%Y%m%d_%H%M}.docx"
    return _save_with_dialog(doc, filename)


# ═══════════════════════════════════════════════════════
# ОТЧЁТ ПО ТЕМЕ
# ═══════════════════════════════════════════════════════

def _fetch_wiki(topic: str) -> dict:
    """Подтягивает статью из Википедии (не обязательно)."""
    try:
        from logic.web_search import search_wikipedia
        return search_wikipedia(topic, sentences=20)
    except Exception:
        return {"found": False, "title": "", "url": "", "summary": ""}


def _expand_text(base: str, min_chars: int = 8000) -> str:
    """Дополняет текст до заданной длины осмысленными абзацами."""
    extras = [
        "Особое внимание в работе уделено анализу существующих подходов "
        "и их практической применимости в современных условиях.",

        "В ходе исследования были рассмотрены как теоретические аспекты "
        "темы, так и примеры практической реализации.",

        "Проведённый анализ показывает, что рассматриваемый вопрос "
        "требует комплексного подхода и учёта множества факторов.",

        "Материалы, представленные в работе, могут быть использованы "
        "для дальнейшего изучения темы и в практической деятельности.",

        "Дополнительно были изучены смежные области, что позволило "
        "сформировать целостное представление о предмете исследования.",

        "Следует отметить, что тема сохраняет актуальность и вызывает "
        "устойчивый интерес как в научной среде, так и на практике.",

        "Обобщение полученных данных позволяет сделать вывод о значимости "
        "рассматриваемого вопроса для современной науки и техники.",

        "Изучение вопроса показало наличие нескольких перспективных "
        "направлений для дальнейших исследований.",
    ]
    text = base
    i = 0
    while len(text) < min_chars and i < len(extras) * 3:
        text += "\n\n" + extras[i % len(extras)]
        i += 1
    return text


def generate_report(
    topic: str = "Тема работы",
    student: str = "Иванов И.И.",
    group: str = "ИС-21",
    teacher: str = "Петров П.П.",
    subject: str = "Информатика",
    **kwargs,
) -> str:
    """Создаёт отчёт по теме (до 10 000 символов) и открывает диалог сохранения."""
    if not DOCX_AVAILABLE:
        return "❌ Установи python-docx: python -m pip install python-docx"

    wiki = _fetch_wiki(topic)
    wiki_text = wiki.get("summary", "") if wiki.get("found") else ""

    # ─── Введение ───
    intro = (
        f"Актуальность темы «{topic}» обусловлена необходимостью глубокого "
        f"изучения данного вопроса в современной науке и практике. "
        f"В работе рассматриваются ключевые аспекты темы, анализируются "
        f"основные подходы и формулируются выводы.\n\n"
        f"Цель работы — изучить тему «{topic}» и представить её системное "
        f"описание.\n\n"
        f"Задачи работы:\n"
        f"1. Изучить теоретические основы темы.\n"
        f"2. Проанализировать существующие подходы и материалы.\n"
        f"3. Сформулировать выводы по результатам исследования.\n\n"
        f"Объект исследования — {topic}.\n"
        f"Предмет исследования — особенности и закономерности, связанные "
        f"с данной темой.\n\n"
        f"Методы исследования: анализ литературы, обобщение, систематизация."
    )

    # ─── Теория ───
    theory_base = f"Теоретическая часть работы посвящена раскрытию темы «{topic}».\n\n"
    if wiki_text:
        theory_base += wiki_text + "\n\n"
    else:
        theory_base += (
            f"В рамках данной темы рассматриваются основные понятия, "
            f"определения и подходы. Тема «{topic}» имеет важное значение "
            f"в современной науке и находит практическое применение "
            f"в различных областях.\n\n"
        )
    theory_base += (
        f"Ключевые аспекты темы:\n"
        f"• Основные понятия и определения\n"
        f"• Исторический контекст\n"
        f"• Современное состояние вопроса\n"
        f"• Практическое применение\n"
        f"• Перспективы развития\n\n"
        f"Анализ показывает, что тема «{topic}» является многогранной "
        f"и требует комплексного подхода к изучению."
    )
    theory = _expand_text(theory_base, min_chars=3500)

    # ─── Практика ───
    practice_base = (
        f"Практическая часть работы посвящена применению теоретических "
        f"знаний по теме «{topic}».\n\n"
        f"Методика исследования включает:\n"
        f"1. Сбор и систематизацию материала по теме.\n"
        f"2. Анализ полученных данных.\n"
        f"3. Сравнение с существующими подходами.\n"
        f"4. Формулирование выводов.\n\n"
        f"В ходе работы были рассмотрены конкретные примеры, "
        f"иллюстрирующие основные положения темы."
    )
    practice = _expand_text(practice_base, min_chars=2500)

    # ─── Заключение ───
    conclusion = (
        f"В ходе работы по теме «{topic}» были достигнуты поставленные "
        f"цели и решены задачи.\n\n"
        f"Основные выводы:\n"
        f"1. Тема «{topic}» имеет важное теоретическое и практическое "
        f"значение.\n"
        f"2. Существующие подходы позволяют эффективно решать задачи "
        f"в данной области.\n"
        f"3. Дальнейшее изучение темы может быть связано с расширением "
        f"практического применения.\n\n"
        f"Практическая значимость работы заключается в возможности "
        f"использования полученных результатов в учебной и "
        f"профессиональной деятельности."
    )

    # ─── Источники ───
    sources = [
        "Иванов И.И. Основы теории. — М.: Наука, 2024. — 350 с.",
        "Петров П.П. Современные подходы // Научный журнал. — 2023. — № 5. — С. 10–25.",
    ]
    if wiki.get("found"):
        sources.append(
            f"Википедия: статья «{wiki['title']}». "
            f"URL: {wiki['url']} (дата обращения: {datetime.now():%d.%m.%Y})."
        )
    sources.append("Официальный портал знаний: https://ru.wikipedia.org")

    # ─── Сборка документа ───
    doc = _setup_doc()

    # Титульный лист (сокращённый)
    _center(doc, "Министерство науки и высшего образования РФ", size=12)
    _center(doc, "")
    for _ in range(3):
        _center(doc, "")
    _center(doc, "ОТЧЁТ", bold=True, size=16)
    _center(doc, f"по дисциплине «{subject}»")
    _center(doc, f"на тему: «{topic}»")
    for _ in range(4):
        _center(doc, "")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(f"Выполнил: студент группы {group}\n{student}\n\n")
    p.add_run(f"Проверил:\n{teacher}")
    for _ in range(4):
        _center(doc, "")
    _center(doc, f"Москва, {datetime.now().year}")
    doc.add_page_break()

    # Содержание
    _heading(doc, "Содержание")
    toc = [
        "Введение",
        "1. Теоретическая часть",
        "   1.1. Основные понятия темы",
        "   1.2. Обзор литературы",
        "2. Практическая часть",
        "   2.1. Методика исследования",
        "   2.2. Результаты",
        "Заключение",
        "Список использованных источников",
    ]
    for item in toc:
        p = doc.add_paragraph(item)
        p.paragraph_format.line_spacing = 1.5
    doc.add_page_break()

    # Введение
    _heading(doc, "Введение")
    for para in intro.split("\n\n"):
        _body(doc, para)

    # Теория
    _heading(doc, "1. Теоретическая часть")
    _subheading(doc, f"1.1. Основные понятия темы «{topic}»")
    for para in theory.split("\n\n"):
        _body(doc, para)

    _subheading(doc, "1.2. Обзор литературы")
    _body(doc,
          "Вопрос, связанный с темой, рассматривался в работах "
          "отечественных и зарубежных исследователей. Ниже приведены "
          "основные источники, которые легли в основу работы.")

    # Практика
    _heading(doc, "2. Практическая часть")
    _subheading(doc, "2.1. Методика исследования")
    for para in practice.split("\n\n"):
        _body(doc, para)

    _subheading(doc, "2.2. Результаты")
    _body(doc,
          "По результатам работы сформулированы основные выводы, "
          "представленные в заключении.")

    # Заключение
    _heading(doc, "Заключение")
    for para in conclusion.split("\n\n"):
        _body(doc, para)

    # Источники
    _heading(doc, "Список использованных источников")
    for i, src in enumerate(sources, 1):
        p = doc.add_paragraph(f"{i}. {src}")
        p.paragraph_format.line_spacing = 1.5

    # Проверка размера
    total_chars = len(intro) + len(theory) + len(practice) + len(conclusion)

    filename = f"Отчёт_{topic[:30].replace(' ', '_')}_{datetime.now():%Y%m%d_%H%M}.docx"
    result = _save_with_dialog(doc, filename)
    return f"{result}\n📊 Объём текста: ~{total_chars} символов"


# ═══════════════════════════════════════════════════════
# ПЛАН РАБОТЫ
# ═══════════════════════════════════════════════════════

def suggest_outline(topic: str) -> str:
    return f"""📝 План работы по теме «{topic}»:

ВВЕДЕНИЕ
  • Актуальность темы
  • Цель и задачи
  • Объект и предмет исследования

1. ТЕОРЕТИЧЕСКАЯ ЧАСТЬ
  1.1. Основные понятия и определения
  1.2. История изучения вопроса
  1.3. Обзор существующих подходов

2. ПРАКТИЧЕСКАЯ ЧАСТЬ
  2.1. Методика исследования
  2.2. Анализ данных
  2.3. Результаты

ЗАКЛЮЧЕНИЕ
  • Основные выводы
  • Практическая значимость

СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ

💡 Заполни тему в форме и нажми «Создать отчёт» — получишь заготовку."""

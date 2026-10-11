# 🧠 МосНейро

Локальный интеллектуальный помощник для учёбы и работы. Работает **без API-ключей** и подписок.

## ✨ Возможности

- 💬 **Чат-бот** — отвечает на вопросы, переводит слова, помнит контекст диалога
- 🌐 **Поиск в сети** — Википедия и DuckDuckGo без API-ключей
- 🧮 **Инженерный расчёт** — калькулятор, символьные вычисления, единицы, шаблоны, графики
- ⚛️ **Физика: лаборатория** — 30+ формул, решение задач по шагам, конвертация величин
- 📚 **Документы** — чтение PDF, DOCX, TXT с поиском по страницам
- 📖 **Библиотека** — индексация папки (FTS5 + семантический поиск)
- 📄 **ГОСТ-документы** — генерация титульников и отчётов по ГОСТ 7.32-2017
- 🖼️ **OCR** — распознавание текста с картинок (без Tesseract)
- 💾 **Экспорт** — сохранение чатов в Markdown

## 🚀 Установка

### 1. Клонировать репозиторий

```bash
git clone git@github.com:ksenianadbitova/Mos_Neiro.git
cd Mos_Neiro

### 2. Создать виртуальное окружение

Windows (PowerShell):

powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
Linux/Mac:

bash
python3 -m venv venv
source venv/bin/activate

### 3. Установить зависимости

bash
python -m pip install -r requirements.txt

### 4. Запустить

bash
python main.py
📁 Структура
text
мос_нейро/
├── main.py                # Точка входа
├── theme.py               # Палитра и шрифты
├── config.py              # Проверка окружения
├── database.py            # SQLite: история и сессии
├── requirements.txt       # Зависимости
│
├── logic/                 # Бизнес-логика
│   ├── math_tutor.py
│   ├── math_templates.py
│   ├── physics_tutor.py
│   ├── physics_templates.py
│   ├── chatbot.py
│   ├── web_search.py
│   ├── units_converter.py
│   ├── image_reader.py
│   ├── document_reader.py
│   ├── library.py
│   ├── semantic_search.py
│   ├── knowledge_base.py
│   ├── gost_helper.py
│   └── exporter.py
│
├── ui/                    # Интерфейс
│   ├── app.py
│   ├── sidebar.py
│   ├── home_screen.py
│   ├── math_screen.py
│   ├── physics_screen.py
│   ├── chatbot_screen.py
│   ├── web_screen.py
│   ├── documents_screen.py
│   ├── library_screen.py
│   ├── gost_screen.py
│   └── settings_screen.py
│
└── knowledge/             # Примеры базы знаний

## 🛠️ Технологии

Python 3.11+

CustomTkinter — современный GUI

SymPy — символьная математика

pint — единицы измерения

matplotlib — графики

wikipedia-api, ddgs — поиск без ключей

deep-translator, argostranslate — перевод (онлайн + офлайн)

rapidocr-onnxruntime — OCR без Tesseract

pymupdf, python-docx — чтение документов

sentence-transformers, chromadb — семантический поиск

SQLite — хранение истории

## 📝 Лицензия

MIT

## 👤 Автор

Ксения Надбитова — @ksenianadbitova
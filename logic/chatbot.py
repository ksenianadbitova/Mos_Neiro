"""Чат-бот с контекстом диалога."""
import random
from logic.web_search import (
    explain_topic, is_translate_request, translate_text, _extract_for_translate,
)


GREETINGS = [
    "Привет! 👋 Чем помочь сегодня?",
    "Здравствуй! Готов помочь с учёбой 📚",
    "Салют! О чём поговорим?",
]
THANKS = ["Всегда пожалуйста! 🙌", "Рад был помочь!", "Не за что!"]
BYE = ["Пока! Удачи 👋", "До встречи!"]
SMALL_TALK = [
    "Спроси конкретнее — я поищу ответ 🔍",
    "Давай разберёмся вместе!",
    "Готов помочь! О чём хочешь узнать?",
]

HELP_TEXT = """📖 Что я умею:

1. Отвечать на вопросы по любому предмету
2. Искать определения и термины
3. Переводить слова («переведи hello»)
4. Распознавать текст с картинок (📎)
5. Помнить контекст — можно уточнять

Примеры:
• Что такое Python?
• Закон Ома
• Переведи hello
• А подробнее?
"""

# Слова-уточнения — когда пользователь ссылается на предыдущее
FOLLOWUP_MARKERS = [
    "подробнее", "подробней", "ещё", "еще", "дальше", "продолжи",
    "а что", "а как", "а почему", "и что", "расскажи больше",
    "объясни лучше", "поподробнее", "детальнее",
]


def _has(text, *words):
    t = text.lower()
    return any(w in t for w in words)


def is_greeting(t):
    t = t.strip().lower()
    return t in {"привет", "здравствуй", "хай", "hello", "hi",
                 "салют", "добрый день", "добрый вечер"}


def is_thanks(t):
    return t.strip().lower() in {"спасибо", "благодарю", "спс", "thanks"}


def is_bye(t):
    return t.strip().lower() in {"пока", "до свидания", "бай", "bye"}


def is_help(t):
    return _has(t, "помощь", "что умеешь", "help", "команды")


def is_followup(t):
    """Проверяет, ссылается ли сообщение на предыдущий ответ."""
    return _has(t, *FOLLOWUP_MARKERS)


def is_question(t):
    t = t.strip().lower()
    if t.endswith("?"):
        return True
    starters = ("что", "как", "почему", "зачем", "когда", "где", "кто",
                "какой", "какая", "объясни", "расскажи", "помоги", "найди",
                "покажи", "сколько", "чем", "переведи", "перевод")
    return t.startswith(starters)


def is_term(t):
    words = t.strip().split()
    return 1 <= len(words) <= 4


def _get_last_user_topic(history):
    """Находит последнюю тему пользователя в истории."""
    if not history:
        return None
    # Ищем последнее сообщение пользователя, которое не было уточнением
    for msg in reversed(history):
        if msg.get("role") == "user":
            content = msg.get("content", "").strip()
            if content and not is_followup(content.lower()):
                return content
    return None


def reply(message: str, history: list = None) -> str:
    """
    Отвечает на сообщение.
    history — список прошлых сообщений [{'role': 'user'/'assistant', 'content': '...'}].
    """
    if not message or not message.strip():
        return "🤔 Ты ничего не написал."

    msg = message.strip()
    low = msg.lower()

    # Перевод — приоритет
    if is_translate_request(low):
        return explain_topic(msg)

    if is_help(low):
        return HELP_TEXT
    if is_greeting(low):
        return random.choice(GREETINGS)
    if is_thanks(low):
        return random.choice(THANKS)
    if is_bye(low):
        return random.choice(BYE)

    # Уточнение — ищем в контексте
    if is_followup(low) and history:
        last_topic = _get_last_user_topic(history)
        if last_topic:
            # Ищем более подробную информацию по прошлой теме
            try:
                detailed = explain_topic(last_topic)
                if detailed and "Не нашёл" not in detailed:
                    return f"🔍 Уточняю по теме «{last_topic}»:\n\n{detailed}"
            except Exception:
                pass

    if is_question(msg) or is_term(msg):
        try:
            return explain_topic(msg)
        except Exception as e:
            return f"😕 Ошибка: {e}"

    return random.choice(SMALL_TALK)


def reply_with_image(image_path: str, user_text: str = "") -> str:
    """Обработка картинки."""
    try:
        from logic.image_reader import analyze_image
    except ImportError:
        return "📎 Картинка получена, но OCR не установлен."

    try:
        result = analyze_image(image_path)
    except Exception as e:
        return f"😕 Ошибка обработки: {e}"

    if result.get("error"):
        return f"😕 Не смог открыть картинку: {result['error']}"

    text = (result.get("text") or "").strip()
    filename = result.get("filename", "изображение")

    parts = [f"📎 Ты прислал: {filename}"]

    if not text:
        parts.append("\n🤔 Текст не распознан.")
        if user_text.strip():
            parts.append("\n\n" + reply(user_text))
        return "\n".join(parts)

    parts.append(f"\n📖 Распознанный текст:\n\n{text}")
    query = user_text.strip() if user_text.strip() else text[:200]
    try:
        answer = explain_topic(query)
        if answer and "Не нашёл" not in answer:
            parts.append(f"\n\n💡 Возможный ответ:\n\n{answer}")
    except Exception:
        pass
    return "\n".join(parts)


def list_examples() -> str:
    return """💡 Попробуй:

• Что такое Python?
• Закон Ома
• Переведи hello
• А подробнее? (уточнение)

📎 Или прикрепи картинку с текстом.
"""

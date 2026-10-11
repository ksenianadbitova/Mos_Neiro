"""
Поиск в сети — как Яндекс.Браузер, но внутри приложения.
Работает без ключей и API через duckduckgo-search.
"""
import customtkinter as ctk
import threading
import webbrowser
from logic.web_search import search_web, translate_text, is_translate_request
from theme import (
    ACCENT, ACCENT_HOVER, BG_CARD, BG_CARD_HOVER, BG_INPUT,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    FONT_FAMILY, SUCCESS, ERROR,
)


class WebScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Заголовок
        ctk.CTkLabel(self, text="🌐 Поиск в сети",
                     font=(FONT_FAMILY, 24, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(20, 4))
        ctk.CTkLabel(self,
                     text="Ищи что угодно: термины, переводы, учебники, статьи",
                     font=(FONT_FAMILY, 12),
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=30, pady=(0, 10))

        # Строка поиска
        search_box = ctk.CTkFrame(self, fg_color="transparent")
        search_box.pack(fill="x", padx=30, pady=(0, 10))

        self.entry = ctk.CTkEntry(
            search_box, height=48,
            font=(FONT_FAMILY, 14),
            placeholder_text="Введи запрос — слово, вопрос, перевод...",
            fg_color=BG_INPUT, corner_radius=24, border_width=0,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.search())

        ctk.CTkButton(
            search_box, text="🔍 Найти", width=120, height=48,
            font=(FONT_FAMILY, 14, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            corner_radius=24,
            command=self.search,
        ).pack(side="left")

        # Быстрые кнопки
        tags = ctk.CTkFrame(self, fg_color="transparent")
        tags.pack(fill="x", padx=30, pady=(4, 10))

        quick = [
            ("Перевести hello", "переведи hello"),
            ("Что такое фотосинтез?", "что такое фотосинтез"),
            ("Учебник Python", "Python учебник pdf"),
            ("Закон Ома", "закон Ома"),
        ]
        for label, q in quick:
            ctk.CTkButton(
                tags, text=label, height=28,
                font=(FONT_FAMILY, 11),
                fg_color=BG_CARD, hover_color=ACCENT,
                text_color=TEXT_SECONDARY, corner_radius=14,
                command=lambda query=q: self.quick_search(query),
            ).pack(side="left", padx=4)

        # Результаты (скролл)
        self.results = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        self._show_welcome()

    def _show_welcome(self):
        card = ctk.CTkFrame(self.results, fg_color=BG_CARD, corner_radius=16)
        card.pack(fill="x", pady=8)
        ctk.CTkLabel(card, text="👋 Привет!",
                     font=(FONT_FAMILY, 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 4))
        ctk.CTkLabel(card,
                     text="Введи любой запрос — я найду:\n"
                          "• Определения и термины (Википедия)\n"
                          "• Учебники, статьи, курсы (веб-поиск)\n"
                          "• Переводы слов (встроенный переводчик)\n\n"
                          "Нажми на карточку результата, чтобы открыть сайт в браузере.",
                     font=(FONT_FAMILY, 13),
                     text_color=TEXT_SECONDARY, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

    def quick_search(self, query):
        self.entry.delete(0, "end")
        self.entry.insert(0, query)
        self.search()

    def search(self):
        query = self.entry.get().strip()
        if not query:
            return

        for w in self.results.winfo_children():
            w.destroy()

        # Проверяем перевод
        if is_translate_request(query):
            self._handle_translate(query)
            return

        # Иначе — обычный поиск
        ctk.CTkLabel(self.results, text=f"🔎 Ищу «{query}»...",
                     font=(FONT_FAMILY, 13, "italic"),
                     text_color=TEXT_SECONDARY).pack(pady=20)
        threading.Thread(target=self._do_search, args=(query,), daemon=True).start()

    def _handle_translate(self, query):
        # Убираем "переведи" и т.д.
        import re
        text = query
        for marker in ["переведи", "перевод", "translate", "перевести", "как переводится"]:
            text = re.sub(marker, "", text, flags=re.IGNORECASE).strip()
        text = text.strip("\"'«»")

        card = ctk.CTkFrame(self.results, fg_color=BG_CARD, corner_radius=14)
        card.pack(fill="x", pady=8)

        ctk.CTkLabel(card, text="🌐 Перевод",
                     font=(FONT_FAMILY, 14, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(14, 4))

        # Определяем направление
        import re as _re
        if _re.search(r"[а-яА-Я]", text):
            translated = translate_text(text, target="en")
            direction = "🇷🇺 → 🇬🇧"
        else:
            translated = translate_text(text, target="ru")
            direction = "🇬🇧 → 🇷🇺"

        if translated:
            ctk.CTkLabel(card, text=f"{direction}  {text}",
                         font=(FONT_FAMILY, 13),
                         text_color=TEXT_MUTED).pack(anchor="w", padx=20)
            ctk.CTkLabel(card, text=translated,
                         font=(FONT_FAMILY, 20, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(4, 16))
        else:
            ctk.CTkLabel(card, text="❌ Не удалось перевести",
                         font=(FONT_FAMILY, 13),
                         text_color=ERROR).pack(anchor="w", padx=20, pady=(4, 16))

    def _do_search(self, query):
        try:
            results = search_web(query, max_results=12)
        except Exception as e:
            results = [{"title": f"Ошибка: {e}", "url": "", "snippet": "", "source": ""}]
        self.after(0, lambda: self._show_results(query, results))

    def _show_results(self, query, results):
        for w in self.results.winfo_children():
            w.destroy()

        if not results or (len(results) == 1 and not results[0].get("url")):
            ctk.CTkLabel(self.results,
                         text="😕 Ничего не нашлось. Попробуй другой запрос.",
                         font=(FONT_FAMILY, 14), text_color=ERROR).pack(pady=20)
            return

        ctk.CTkLabel(self.results, text=f"Найдено: {len(results)}",
                     font=(FONT_FAMILY, 12),
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(0, 6))

        for item in results:
            self._make_card(item)

    def _make_card(self, item):
        card = ctk.CTkFrame(self.results, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="x", pady=5)

        # Источник (метка)
        source = item.get("source", "")
        if source:
            color = ACCENT if source == "Википедия" else SUCCESS
            ctk.CTkLabel(card, text=f"  {source}  ",
                         font=(FONT_FAMILY, 10, "bold"),
                         text_color="#FFFFFF", fg_color=color,
                         corner_radius=8).pack(anchor="w", padx=16, pady=(10, 4))

        # Заголовок (кликабельный)
        url = item.get("url", "")
        title_btn = ctk.CTkButton(
            card, text=item.get("title", "(без названия)"),
            font=(FONT_FAMILY, 14, "bold"),
            text_color=ACCENT,
            fg_color="transparent", hover_color=BG_CARD_HOVER,
            anchor="w", height=28,
            command=lambda u=url: webbrowser.open(u) if u else None,
        )
        title_btn.pack(fill="x", padx=16, pady=(4, 0))

        # URL
        if url:
            ctk.CTkLabel(card, text=url,
                         font=(FONT_FAMILY, 11),
                         text_color=TEXT_MUTED, anchor="w").pack(fill="x", padx=16)

        # Сниппет
        if item.get("snippet"):
            ctk.CTkLabel(card, text=item["snippet"],
                         font=(FONT_FAMILY, 12),
                         text_color=TEXT_SECONDARY,
                         wraplength=900, justify="left", anchor="w").pack(fill="x", padx=16, pady=(4, 6))

        # Кнопки
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkButton(row, text="🔗 Открыть", width=110, height=28,
                      font=(FONT_FAMILY, 11),
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      command=lambda u=url: webbrowser.open(u) if u else None,
                      ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(row, text="📋 Скопировать ссылку", width=160, height=28,
                      font=(FONT_FAMILY, 11),
                      fg_color=BG_CARD_HOVER, hover_color=ACCENT,
                      text_color=TEXT_SECONDARY,
                      command=lambda u=url: self._copy(u),
                      ).pack(side="left")

    def _copy(self, text):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception:
            pass

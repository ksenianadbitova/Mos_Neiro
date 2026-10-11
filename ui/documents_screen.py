import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from logic.document_reader import read_file, search_in_document, get_summary
import theme


class DocumentsScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.current_file = None

        # Заголовок
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(30, 10))
        ctk.CTkLabel(header, text="📚 Документы",
                     font=(theme.FONT_FAMILY, 28, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Загрузи PDF, DOCX или TXT и задай вопрос по содержимому",
                     font=(theme.FONT_FAMILY, 13),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 0))

        # Верхняя панель с кнопкой загрузки
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=50, pady=(12, 6))

        ctk.CTkButton(
            top, text="📂 Загрузить файл", width=180, height=40,
            font=(theme.FONT_FAMILY, 13, "bold"),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", corner_radius=20,
            command=self.load_file,
        ).pack(side="left", padx=4)

        self.file_label = ctk.CTkLabel(
            top, text="Файл не выбран",
            font=(theme.FONT_FAMILY, 12),
            text_color=theme.TEXT_SECONDARY,
        )
        self.file_label.pack(side="left", padx=12)

        # Поле поиска по документу
        search_box = ctk.CTkFrame(self, fg_color=theme.BG_CARD,
                                  corner_radius=20, border_width=1,
                                  border_color=theme.BORDER)
        search_box.pack(fill="x", padx=50, pady=(12, 6))

        self.query_entry = ctk.CTkEntry(
            search_box, height=40, font=(theme.FONT_FAMILY, 14),
            placeholder_text="Что искать в документе?",
            fg_color="transparent", border_width=0,
            text_color=theme.TEXT_PRIMARY,
        )
        self.query_entry.pack(side="left", fill="x", expand=True, padx=16, pady=8)
        self.query_entry.bind("<Return>", lambda e: self.search_in_doc())

        ctk.CTkButton(
            search_box, text="🔍 Найти", width=100, height=40,
            font=(theme.FONT_FAMILY, 13, "bold"),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", corner_radius=20,
            command=self.search_in_doc,
        ).pack(side="right", padx=8, pady=8)

        # Область вывода
        self.output = ctk.CTkTextbox(
            self, font=(theme.FONT_FAMILY, 13),
            fg_color=theme.BG_CARD, text_color=theme.TEXT_PRIMARY,
            corner_radius=12, wrap="word", border_width=1,
            border_color=theme.BORDER,
        )
        self.output.pack(fill="both", expand=True, padx=50, pady=(10, 30))

        self._show_welcome()

    def _show_welcome(self):
        text = (
            "👋 Привет!\n\n"
            "Загрузи учебник (PDF), конспект (DOCX) или текстовый файл — "
            "и я помогу найти в нём нужную информацию.\n\n"
            "💡 Примеры:\n"
            "  • Загрузи учебник физики → спроси «закон Ома»\n"
            "  • Загрузи конспект → спроси «что такое интеграл»\n"
            "  • Загрузи методичку → спроси «формула скорости»\n\n"
            "Результаты показываются с указанием номера страницы.\n\n"
            "📂 Поддерживаются: PDF, DOCX, TXT, MD"
        )
        self._log(text, clear=True)

    def _log(self, text, clear=False):
        if clear:
            self.output.delete("1.0", "end")
        self.output.insert("end", text + "\n")
        self.output.see("end")

    def load_file(self):
        path = filedialog.askopenfilename(
            title="Выбери документ",
            filetypes=[
                ("Все поддерживаемые", "*.pdf *.docx *.txt *.md"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("Текст", "*.txt *.md"),
                ("Все файлы", "*.*"),
            ],
        )
        if not path:
            return

        self.current_file = path
        self.file_label.configure(text=f"📄 {Path(path).name}")

        self._log(f"⏳ Читаю файл: {Path(path).name}...\n", clear=True)

        try:
            summary = get_summary(path, max_chars=800)
            self._log(summary)
            self._log("\n💡 Теперь можешь задать вопрос в поле выше.")
        except Exception as e:
            self._log(f"❌ Ошибка: {e}")

    def search_in_doc(self):
        if not self.current_file:
            self._log("⚠️ Сначала загрузи файл (кнопка «📂 Загрузить файл»).", clear=True)
            return

        query = self.query_entry.get().strip()
        if not query:
            self._log("⚠️ Введи поисковый запрос.", clear=True)
            return

        self._log(f"🔍 Ищу «{query}» в {Path(self.current_file).name}...\n", clear=True)

        try:
            results = search_in_document(self.current_file, query)
        except Exception as e:
            self._log(f"❌ Ошибка поиска: {e}")
            return

        if not results:
            self._log(
                f"😕 По запросу «{query}» ничего не найдено.\n\n"
                f"💡 Попробуй:\n"
                f"  • Другие слова\n"
                f"  • Более короткий запрос\n"
                f"  • Синонимы"
            )
            return

        self._log(f"✅ Найдено фрагментов: {len(results)}\n")
        self._log("─" * 60 + "\n")

        for i, item in enumerate(results, 1):
            page = item.get("page", "?")
            text = item.get("text", "")
            score = item.get("score", 0)
            confidence = "высокая" if score > 0.6 else "средняя" if score > 0.4 else "низкая"

            self._log(f"📄 Фрагмент {i} (стр. {page}, релевантность: {confidence})")
            self._log("")
            self._log(text)
            self._log("")
            self._log("─" * 60 + "\n")

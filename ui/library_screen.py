import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import webbrowser
from pathlib import Path
from logic.library import (
    init_library, index_folder, search_library,
    list_indexed, clear_library, library_stats,
)
try:
    from logic.semantic_search import (
        index_folder_semantic, search_semantic,
        semantic_stats, is_available as sem_available,
    )
    SEMANTIC_OK = True
except Exception:
    SEMANTIC_OK = False

import theme


class LibraryScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.current_folder = None

        # Заголовок
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(30, 10))
        ctk.CTkLabel(header, text="📖 Библиотека",
                     font=(theme.FONT_FAMILY, 28, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header,
                     text="Проиндексируй папку с учебниками и ищи по всем документам сразу",
                     font=(theme.FONT_FAMILY, 13),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 0))

        # Панель действий
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=50, pady=(12, 6))

        ctk.CTkButton(
            actions, text="📂 Выбрать папку и проиндексировать",
            height=38, width=280,
            font=(theme.FONT_FAMILY, 13, "bold"),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", corner_radius=19,
            command=self.pick_folder,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            actions, text="📋 Список документов",
            height=38, width=180,
            font=(theme.FONT_FAMILY, 12),
            fg_color=theme.BG_CARD, hover_color=theme.ACCENT_LIGHT,
            text_color=theme.TEXT_SECONDARY, corner_radius=19,
            border_width=1, border_color=theme.BORDER,
            command=self.show_documents,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions, text="🧠 Семант. индексация",
            height=38, width=200,
            font=(theme.FONT_FAMILY, 12),
            fg_color=theme.BG_CARD, hover_color=theme.ACCENT_LIGHT,
            text_color=theme.TEXT_SECONDARY, corner_radius=19,
            border_width=1, border_color=theme.BORDER,
            command=self.semantic_index,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            actions, text="🗑 Очистить",
            height=38, width=120,
            font=(theme.FONT_FAMILY, 12),
            fg_color=theme.BG_CARD, hover_color=theme.ERROR,
            text_color=theme.TEXT_SECONDARY, corner_radius=19,
            border_width=1, border_color=theme.BORDER,
            command=self.clear_lib,
        ).pack(side="left", padx=4)

        # Статистика
        self.stats_label = ctk.CTkLabel(
            self, text="",
            font=(theme.FONT_FAMILY, 12),
            text_color=theme.TEXT_MUTED,
        )
        self.stats_label.pack(anchor="w", padx=50, pady=(0, 6))

        # Строка поиска
        search_box = ctk.CTkFrame(self, fg_color=theme.BG_CARD,
                                  corner_radius=20, border_width=1,
                                  border_color=theme.BORDER)
        search_box.pack(fill="x", padx=50, pady=(6, 6))

        self.query_entry = ctk.CTkEntry(
            search_box, height=40, font=(theme.FONT_FAMILY, 14),
            placeholder_text="Что искать во всех документах?",
            fg_color="transparent", border_width=0,
            text_color=theme.TEXT_PRIMARY,
        )
        self.query_entry.pack(side="left", fill="x", expand=True, padx=16, pady=8)
        self.query_entry.bind("<Return>", lambda e: self.do_search())

        ctk.CTkButton(
            search_box, text="🔍 Найти", width=110, height=40,
            font=(theme.FONT_FAMILY, 13, "bold"),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", corner_radius=20,
            command=self.do_search,
        ).pack(side="right", padx=8, pady=8)

        # Прогресс-бар
        self.progress = ctk.CTkProgressBar(self, height=6)
        self.progress.pack(fill="x", padx=50, pady=(0, 4))
        self.progress.set(0)

        # Область вывода
        self.output = ctk.CTkTextbox(
            self, font=(theme.FONT_FAMILY, 13),
            fg_color=theme.BG_CARD, text_color=theme.TEXT_PRIMARY,
            corner_radius=12, wrap="word", border_width=1,
            border_color=theme.BORDER,
        )
        self.output.pack(fill="both", expand=True, padx=50, pady=(0, 30))

        # Инициализация
        init_library()
        self.update_stats()
        self._log_welcome()

    def _log_welcome(self):
        text = (
            "👋 Это раздел «Библиотека».\n\n"
            "Что делает:\n"
            "  1. Ты выбираешь папку со своими PDF/DOCX/TXT\n"
            "  2. Программа индексирует все файлы (один раз)\n"
            "  3. Дальше ищешь по всем документам сразу — как в поисковике\n\n"
            "💡 Пример использования:\n"
            "  • Скачай 5-10 учебников в одну папку\n"
            "  • Нажми «📂 Выбрать папку и проиндексировать»\n"
            "  • Ищи «закон Ома» — найдётся во всех книгах с номером страницы\n\n"
            "📂 Поддерживаются: PDF, DOCX, TXT, MD\n\n"
            "Начни с кнопки «📂 Выбрать папку и проиндексировать»."
        )
        self._log(text, clear=True)

    def _log(self, text, clear=False):
        if clear:
            self.output.delete("1.0", "end")
        self.output.insert("end", text + "\n")
        self.output.see("end")

    def update_stats(self):
        try:
            s = library_stats()
            self.stats_label.configure(
                text=f"📊 В библиотеке: {s['docs']} документов, "
                     f"{s['pages']} страниц, {s['chars']:,} символов"
                     .replace(",", " ")
            )
        except Exception:
            self.stats_label.configure(text="")

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Выбери папку с документами")
        if not folder:
            return
        self.current_folder = folder
        self._log(f"\n📂 Индексирую папку: {folder}\n", clear=True)
        self.progress.set(0)

        # Индексация в фоне
        threading.Thread(target=self._do_index, args=(folder,), daemon=True).start()

    def _do_index(self, folder):
        def progress_cb(i, total, name):
            try:
                self.progress.set(i / total if total else 0)
                if i % 5 == 0 or i == total:
                    self.after(0, lambda: self._log(f"  [{i}/{total}] {name[:60]}"))
            except Exception:
                pass

        try:
            result = index_folder(folder, progress_cb=progress_cb)
        except Exception as e:
            self.after(0, lambda: self._log(f"\n❌ Ошибка: {e}"))
            return

        self.after(0, lambda: self._show_index_result(result))

    def _show_index_result(self, result):
        self.progress.set(1)
        self._log("\n✅ Индексация завершена!\n")
        self._log(f"   Новых документов: {result.get('indexed', 0)}")
        self._log(f"   Пропущено (уже в базе): {result.get('skipped', 0)}")
        self._log(f"   Всего файлов: {result.get('total', 0)}")
        if result.get("errors"):
            self._log(f"\n⚠️ Ошибок: {len(result['errors'])}")
            for e in result["errors"][:5]:
                self._log(f"   - {e}")
        self.update_stats()

    def show_documents(self):
        try:
            docs = list_indexed()
        except Exception as e:
            self._log(f"❌ Ошибка: {e}", clear=True)
            return

        if not docs:
            self._log("📭 Библиотека пуста. Сначала проиндексируй папку.", clear=True)
            return

        self._log(f"\n📚 Документов в библиотеке: {len(docs)}\n", clear=True)
        for d in docs:
            self._log(f"📄 {d['name']}")
            self._log(f"   Путь: {d['path']}")
            self._log(f"   Тип: {d['type'].upper()}, страниц: {d['pages']}")
            self._log(f"   Индексирован: {d['indexed_at']}")
            self._log("")

    def semantic_index(self):
        """Семантическая индексация выбранной папки."""
        if not SEMANTIC_OK:
            self._log("❌ Семантический поиск недоступен.\n"
                     "Установи: python -m pip install sentence-transformers chromadb", clear=True)
            return

        folder = filedialog.askdirectory(title="Выбери папку для семантической индексации")
        if not folder:
            return

        self._log(f"🧠 Семантическая индексация: {folder}\n"
                 f"(первый запуск скачает модель ~120 МБ)\n", clear=True)

        def progress(i, total, name):
            try:
                self.progress.set(i / total if total else 0)
                if i % 3 == 0 or i == total:
                    self.after(0, lambda: self._log(f"  [{i}/{total}] {name[:60]}"))
            except Exception:
                pass

        def run():
            try:
                result = index_folder_semantic(folder, progress_cb=progress)
                self.after(0, lambda: self._show_semantic_result(result))
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ Ошибка: {e}"))

        threading.Thread(target=run, daemon=True).start()

    def _show_semantic_result(self, result):
        self.progress.set(1)
        self._log("\n✅ Семантическая индексация завершена!")
        self._log(f"   Документов добавлено: {result.get('indexed', 0)}")
        self._log(f"   Чанков создано: {result.get('chunks', 0)}")
        if result.get("errors"):
            self._log(f"\n⚠️ Ошибок: {len(result['errors'])}")
            for e in result["errors"][:3]:
                self._log(f"   - {e}")
        stats = semantic_stats()
        self._log(f"\n📊 Всего чанков в БД: {stats.get('chunks', 0)}")

    def do_semantic_search(self):
        """Поиск по смыслу."""
        if not SEMANTIC_OK:
            self._log("❌ Семантический поиск недоступен.", clear=True)
            return
        query = self.query_entry.get().strip()
        if not query:
            return
        self._log(f"🧠 Семантический поиск: «{query}»\n", clear=True)

        try:
            results = search_semantic(query, top_k=10)
        except Exception as e:
            self._log(f"❌ Ошибка: {e}")
            return

        if not results:
            self._log("😕 Ничего не найдено. Возможно, документы не проиндексированы семантически.")
            return

        self._log(f"✅ Найдено: {len(results)}\n")
        for i, r in enumerate(results, 1):
            self._log(f"📄 {r['doc']} (стр. {r['page']}), релевантность: {r['score']}")
            self._log(f"   {r['text']}")
            self._log("")

    def do_search(self):
        """Поиск: если нажата кнопка - семантический, иначе FTS."""
        query = self.query_entry.get().strip()
        if not query:
            return

        # Простое правило: если в запросе больше 2 слов - семантический
        words = query.split()
        if SEMANTIC_OK and len(words) >= 3:
            return self.do_semantic_search()

        self._log(f"🔍 Ищу «{query}» по всей библиотеке...\n", clear=True)

        try:
            results = search_library(query, limit=15)
        except Exception as e:
            self._log(f"❌ Ошибка поиска: {e}")
            return

        if not results:
            self._log("😕 Ничего не найдено. Попробуй другие слова.")
            return

        if "error" in results[0]:
            self._log(f"❌ Ошибка FTS: {results[0]['error']}")
            return

        self._log(f"✅ Найдено фрагментов: {len(results)}\n")
        self._log("─" * 60)

        for i, r in enumerate(results, 1):
            self._log(f"\n📄 {r['doc']}  (стр. {r['page']})")
            self._log(f"   {r['text']}")
            self._log("")

    def clear_lib(self):
        if not messagebox.askyesno("Очистка", "Удалить все документы из библиотеки?"):
            return
        try:
            clear_library()
            self._log("🗑 Библиотека очищена.", clear=True)
            self.update_stats()
        except Exception as e:
            self._log(f"❌ Ошибка: {e}")

    def do_search(self):
        query = self.query_entry.get().strip()
        if not query:
            return
        self._log(f"🔍 Ищу «{query}» по всей библиотеке...\n", clear=True)

        try:
            results = search_library(query, limit=15)
        except Exception as e:
            self._log(f"❌ Ошибка поиска: {e}")
            return

        if not results:
            self._log("😕 Ничего не найдено. Попробуй другие слова.")
            return

        if "error" in results[0]:
            self._log(f"❌ Ошибка FTS: {results[0]['error']}")
            return

        self._log(f"✅ Найдено фрагментов: {len(results)}\n")
        self._log("─" * 60)

        for i, r in enumerate(results, 1):
            self._log(f"\n📄 {r['doc']}  (стр. {r['page']})")
            self._log(f"   {r['text']}")
            self._log("")

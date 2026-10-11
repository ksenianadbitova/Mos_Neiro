import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from logic.chatbot import reply, list_examples, HELP_TEXT, reply_with_image
from database import (
    create_session, add_message, get_session_messages,
    save_interaction, update_stats,
)
import theme


class Bubble(ctk.CTkFrame):
    def __init__(self, master, text="", is_user=False):
        super().__init__(master, fg_color="transparent")
        if is_user:
            color = theme.ACCENT
            text_color = "#FFFFFF"
            anchor = "e"
            padx = (100, 0)
        else:
            color = theme.BG_CARD
            text_color = theme.TEXT_PRIMARY
            anchor = "w"
            padx = (0, 100)

        b = ctk.CTkFrame(self, fg_color=color, corner_radius=14,
                         border_width=0 if is_user else 1,
                         border_color=theme.BORDER)
        b.pack(anchor=anchor, padx=padx, pady=6)
        ctk.CTkLabel(b, text=text,
                     font=(theme.FONT_FAMILY, 14),
                     text_color=text_color,
                     wraplength=520, justify="left").pack(padx=16, pady=10)


class ChatbotScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pending_image = None
        self.session_id = None  # НОВОЕ: текущая сессия

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=50, pady=(30, 10))
        ctk.CTkLabel(header, text="💬 Чат-бот",
                     font=(theme.FONT_FAMILY, 28, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Спроси что угодно — помню контекст диалога",
                     font=(theme.FONT_FAMILY, 13),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 0))

        ctr = ctk.CTkFrame(self, fg_color="transparent")
        ctr.pack(fill="x", padx=50, pady=(12, 6))

        for text, cmd in [
            ("💡 Примеры", lambda: self._add_safe(list_examples(), False)),
            ("📖 Помощь", lambda: self._add_safe(HELP_TEXT, False)),
            ("🆕 Новый чат", self.new_chat),
            ("💾 Экспорт", self.export_chat),
            ("🧹 Очистить", self.clear),
        ]:
            ctk.CTkButton(
                ctr, text=text, width=120, height=32,
                font=(theme.FONT_FAMILY, 12),
                fg_color=theme.BG_CARD,
                hover_color=theme.ACCENT_LIGHT,
                text_color=theme.TEXT_SECONDARY,
                corner_radius=16,
                border_width=1, border_color=theme.BORDER,
                command=cmd,
            ).pack(side="left", padx=4)

        self.chat = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat.pack(fill="both", expand=True, padx=50, pady=10)

        ib = ctk.CTkFrame(self, fg_color=theme.BG_CARD,
                          corner_radius=24, border_width=1,
                          border_color=theme.BORDER)
        ib.pack(fill="x", padx=50, pady=(0, 30))

        ctk.CTkButton(
            ib, text="📎", width=42, height=42,
            font=(theme.FONT_FAMILY, 18),
            fg_color="transparent", hover_color=theme.BG_CARD_HOVER,
            text_color=theme.TEXT_MUTED, corner_radius=21,
            command=self.pick_image,
        ).pack(side="left", padx=(8, 0), pady=6)

        self.entry = ctk.CTkEntry(
            ib, height=42, font=(theme.FONT_FAMILY, 14),
            placeholder_text="Спросите МосНейро...",
            fg_color="transparent", border_width=0,
            text_color=theme.TEXT_PRIMARY,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self.entry.bind("<Return>", lambda e: self.send())
        # Ctrl+Enter — тоже отправка
        self.entry.bind("<Control-Return>", lambda e: self.send())
        # Ctrl+L перенесён на кнопку, чтобы не ломать CTk

        ctk.CTkButton(
            ib, text="➤", width=42, height=42,
            font=(theme.FONT_FAMILY, 18, "bold"),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            corner_radius=21,
            command=self.send,
        ).pack(side="right", padx=(0, 8), pady=6)

        # Создаём первую сессию и приветствие
        self.new_chat()

    def new_chat(self):
        """Создаёт новую сессию."""
        # Очищаем чат
        try:
            for w in self.chat.winfo_children():
                w.destroy()
        except Exception:
            pass

        # Новая сессия в БД
        try:
            self.session_id = create_session("Новый чат")
        except Exception:
            self.session_id = None

        welcome = (
            "Привет! 👋 Я МосНейро.\n\n"
            "Могу ответить на вопросы, перевести слово, "
            "распознать текст с картинки.\n\n"
            "💡 Помню контекст — можно уточнять: «а подробнее?»"
        )
        self._add_safe(welcome, False)
        # Сохраняем приветствие
        if self.session_id:
            try:
                add_message(self.session_id, "assistant", welcome)
            except Exception:
                pass

    def pick_image(self):
        path = filedialog.askopenfilename(
            title="Выбери картинку",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                       ("Все файлы", "*.*")],
        )
        if not path:
            return
        self.pending_image = path
        filename = Path(path).name
        self.entry.configure(placeholder_text=f"📎 {filename} — добавь вопрос")

    def _add_safe(self, text, is_user=False):
        try:
            if not self.winfo_exists():
                return
            b = Bubble(self.chat, text=text, is_user=is_user)
            b.pack(fill="x", pady=2)
            try:
                self.chat._parent_canvas.yview_moveto(1.0)
            except Exception:
                pass
        except Exception:
            pass

    def send(self):
        msg = self.entry.get().strip()
        img = self.pending_image

        if not msg and not img:
            return

        self._add_safe(msg or "📎 Картинка", True)
        self.entry.delete(0, "end")

        saved_img = img
        self.pending_image = None
        self.entry.configure(placeholder_text="Спросите МосНейро...")

        # Сохраняем сообщение пользователя
        if self.session_id:
            try:
                add_message(self.session_id, "user", msg or "[картинка]")
            except Exception:
                pass

        # Получаем историю диалога
        history = []
        if self.session_id:
            try:
                history = get_session_messages(self.session_id, limit=10)
            except Exception:
                history = []

        # Заглушка «думаю»
        thinking = None
        try:
            thinking = ctk.CTkLabel(
                self.chat, text="🤔 Ищу ответ...",
                font=(theme.FONT_FAMILY, 12, "italic"),
                text_color=theme.TEXT_SECONDARY,
            )
            thinking.pack(anchor="w", padx=10, pady=4)
            self.update()
        except Exception:
            pass

        # Получаем ответ
        try:
            if saved_img:
                ans = reply_with_image(saved_img, msg)
            else:
                ans = reply(msg, history=history)
        except Exception as e:
            ans = f"😕 Ошибка: {e}"

        try:
            if thinking is not None and thinking.winfo_exists():
                thinking.destroy()
        except Exception:
            pass

        self._add_safe(ans, False)

        # Сохраняем ответ бота
        if self.session_id:
            try:
                add_message(self.session_id, "assistant", ans)
            except Exception:
                pass

        try:
            save_interaction("chatbot", msg or "[картинка]", ans)
            update_stats("chatbot", correct=True)
        except Exception:
            pass

    def export_chat(self):
        """Экспортирует текущую сессию в Markdown."""
        if not self.session_id:
            self._add_safe("⚠️ Нет активной сессии", False)
            return
        try:
            from logic.exporter import export_session
            result = export_session(self.session_id, format="md")
            self._add_safe(result, False)
        except Exception as e:
            self._add_safe(f"❌ Ошибка экспорта: {e}", False)

    def clear(self):
        """Очищает текущий чат."""
        if self.session_id:
            try:
                from database import delete_session
                delete_session(self.session_id)
            except Exception:
                pass
        self.new_chat()

import customtkinter as ctk
import theme


class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, on_navigate=None):
        super().__init__(master, fg_color="transparent")
        self.on_navigate = on_navigate

        # ─── Центральный контейнер ───
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True, fill="both")

        # Воздух сверху
        ctk.CTkFrame(center, height=40, fg_color="transparent").pack()

        # Логотип-эмодзи
        ctk.CTkLabel(center, text="🧠",
                     font=(theme.FONT_FAMILY, 64)).pack(pady=(0, 8))

        # Заголовок
        ctk.CTkLabel(center, text="Добро пожаловать!",
                     font=(theme.FONT_FAMILY, 32, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(pady=(0, 6))

        ctk.CTkLabel(center,
                     text="Я МосНейро — твой помощник в учёбе и работе.\n"
                          "Выбери раздел или начни с чата.",
                     font=(theme.FONT_FAMILY, 14),
                     text_color=theme.TEXT_SECONDARY,
                     justify="center").pack(pady=(0, 24))

        # ─── CTA-кнопка ───
        ctk.CTkButton(
            center, text="💬   Начать чат",
            width=240, height=50,
            font=(theme.FONT_FAMILY, 15, "bold"),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", corner_radius=25,
            command=lambda: self.on_navigate("chatbot") if self.on_navigate else None,
        ).pack(pady=(0, 32))

        # ─── Заголовок секции ───
        ctk.CTkLabel(center, text="Разделы",
                     font=(theme.FONT_FAMILY, 11, "bold"),
                     text_color=theme.TEXT_MUTED).pack(pady=(0, 12))

        # ─── Сетка карточек ───
        grid = ctk.CTkFrame(center, fg_color="transparent")
        grid.pack(pady=(0, 40))

        items = [
            ("🧮", "Инженерный расчёт", "Вычисления, единицы, графики", "math"),
            ("⚛️", "Физика: лаборатория", "Формулы, задачи, величины", "physics"),
            ("🌐", "Поиск в сети", "Ответы на любые вопросы", "web"),
            ("📖", "Библиотека", "Поиск по твоим документам", "library"),
            ("📄", "ГОСТ-документы", "Отчёты и титульники", "gost"),
            ("⚙️", "Настройки", "Статус и параметры", "settings"),
        ]

        for i, (icon, title, desc, key) in enumerate(items):
            r, c = divmod(i, 3)
            self._make_card(grid, r, c, icon, title, desc, key)

    def _make_card(self, parent, row, col, icon, title, desc, key):
        card = ctk.CTkFrame(parent, fg_color=theme.BG_CARD,
                             corner_radius=14,
                             border_width=1, border_color=theme.BORDER,
                             width=220, height=130)
        card.grid(row=row, column=col, padx=8, pady=8)
        card.grid_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=16, pady=14)

        ctk.CTkLabel(inner, text=icon,
                     font=(theme.FONT_FAMILY, 26)).pack(anchor="w")
        ctk.CTkLabel(inner, text=title,
                     font=(theme.FONT_FAMILY, 13, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", pady=(6, 2))
        ctk.CTkLabel(inner, text=desc,
                     font=(theme.FONT_FAMILY, 10),
                     text_color=theme.TEXT_MUTED,
                     wraplength=180, justify="left").pack(anchor="w")

        # Hover-эффект
        def on_enter(e):
            card.configure(fg_color=theme.BG_CARD_HOVER, border_color=theme.ACCENT)

        def on_leave(e):
            card.configure(fg_color=theme.BG_CARD, border_color=theme.BORDER)

        for w in [card, inner] + list(inner.winfo_children()):
            w.bind("<Button-1>", lambda e, k=key: self.on_navigate(k) if self.on_navigate else None)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            try:
                w.configure(cursor="hand2")
            except Exception:
                pass

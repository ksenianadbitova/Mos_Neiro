import customtkinter as ctk
import theme


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_select):
        super().__init__(master, width=260, corner_radius=0,
                         fg_color=theme.BG_SIDEBAR)
        self.grid_propagate(False)
        self.on_select = on_select
        self.buttons = {}
        self.indicators = {}
        self.active_key = None

        # ─── Логотип ───
        logo = ctk.CTkFrame(self, fg_color="transparent")
        logo.pack(fill="x", pady=(24, 20), padx=20)

        ctk.CTkLabel(logo, text="🧠",
                     font=(theme.FONT_FAMILY, 28)).pack(side="left", padx=(0, 10))

        box = ctk.CTkFrame(logo, fg_color="transparent")
        box.pack(side="left")
        ctk.CTkLabel(box, text="МосНейро",
                     font=(theme.FONT_FAMILY, 17, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(box, text="нейро-помощник",
                     font=(theme.FONT_FAMILY, 10),
                     text_color=theme.TEXT_MUTED).pack(anchor="w")

        # ─── Кнопка «Новый чат» ───
        ctk.CTkButton(
            self, text="  ✏️    Новый чат",
            height=40, anchor="w",
            font=(theme.FONT_FAMILY, 13, "bold"),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=10,
            command=lambda: self.on_select("chatbot"),
        ).pack(fill="x", padx=16, pady=(0, 16))

        # ─── Меню с группами ───
        self._add_group("ОСНОВНОЕ", [
            ("🏠", "Главная", "home"),
            ("💬", "Чат-бот", "chatbot"),
            ("🌐", "Поиск в сети", "web"),
        ])
        self._add_group("ИНСТРУМЕНТЫ", [
            ("🧮", "Инженерный расчёт", "math"),
            ("⚛️", "Физика: лаборатория", "physics"),
            ("📚", "Документы", "documents"),
            ("📖", "Библиотека", "library"),
            ("📄", "ГОСТ-документы", "gost"),
        ])
        self._add_group("СИСТЕМА", [
            ("⚙️", "Настройки", "settings"),
        ])

        # ─── Подвал ───
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkFrame(self, height=1, fg_color=theme.BORDER).pack(fill="x", padx=16, pady=(6, 10))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(footer, text="🧠", font=(theme.FONT_FAMILY, 20)).pack(side="left", padx=(0, 8))
        info = ctk.CTkFrame(footer, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text="МосНейро",
                     font=(theme.FONT_FAMILY, 11, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info, text="v2.0",
                     font=(theme.FONT_FAMILY, 9),
                     text_color=theme.TEXT_MUTED).pack(anchor="w")

    def _add_group(self, title, items):
        ctk.CTkLabel(self, text=title,
                     font=(theme.FONT_FAMILY, 10, "bold"),
                     text_color=theme.TEXT_MUTED,
                     anchor="w").pack(fill="x", padx=22, pady=(8, 4))

        for icon, label, key in items:
            self._add_button(icon, label, key)

    def _add_button(self, icon, label, key):
        # Контейнер кнопки (для индикатора слева)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=10, pady=1)

        # Индикатор слева (плашка)
        indicator = ctk.CTkFrame(container, width=3, height=36,
                                  fg_color="transparent", corner_radius=2)
        indicator.pack(side="left", padx=(0, 6))

        btn = ctk.CTkButton(
            container,
            text=f"  {icon}    {label}",
            height=40, anchor="w",
            font=(theme.FONT_FAMILY, 13),
            fg_color="transparent",
            hover_color=theme.BG_CARD_HOVER,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=8,
            command=lambda k=key: self.on_select(k),
        )
        btn.pack(side="left", fill="x", expand=True)

        self.buttons[key] = btn
        self.indicators[key] = indicator

    def set_active(self, key):
        # Сброс предыдущего
        if self.active_key and self.active_key in self.buttons:
            try:
                self.buttons[self.active_key].configure(
                    fg_color="transparent",
                    text_color=theme.TEXT_SECONDARY,
                )
                self.indicators[self.active_key].configure(fg_color="transparent")
            except Exception:
                pass

        # Установка нового
        if key in self.buttons:
            try:
                self.buttons[key].configure(
                    fg_color=theme.ACCENT_LIGHT,
                    text_color=theme.ACCENT,
                )
                self.indicators[key].configure(fg_color=theme.ACCENT)
            except Exception:
                pass

        self.active_key = key

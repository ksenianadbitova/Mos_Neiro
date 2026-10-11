import customtkinter as ctk
from logic.gost_helper import (
    get_rules, suggest_outline,
    generate_title_page, generate_report,
)
from theme import (
    ACCENT, ACCENT_HOVER, BG_CARD, BG_INPUT, TEXT_PRIMARY,
    TEXT_SECONDARY, FONT_FAMILY, SUCCESS, WARNING,
)


class GostScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="📄 ГОСТ-документы",
                     font=(FONT_FAMILY, 26, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=40, pady=(30, 4))
        ctk.CTkLabel(self,
                     text="Титульный лист и отчёт по теме — сохраняются через диалог",
                     font=(FONT_FAMILY, 13),
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=40, pady=(0, 16))

        # Табы
        self.tabs = ctk.CTkTabview(
            self, fg_color=BG_CARD,
            segmented_button_fg_color=BG_CARD,
            segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            corner_radius=16, height=440,
        )
        self.tabs.pack(fill="x", padx=40, pady=(0, 10))

        tab1 = self.tabs.add("📄 Титульный лист")
        tab2 = self.tabs.add("📝 Отчёт по теме")

        # ─── Таб 1: Титульник ───
        f1 = ctk.CTkFrame(tab1, fg_color="transparent")
        f1.pack(fill="x", padx=10, pady=10)

        self.title_inputs = {}
        title_fields = [
            ("university", "Учебное заведение", "МГУ им. М.В. Ломоносова"),
            ("faculty", "Факультет", "Факультет ВМК"),
            ("department", "Кафедра", "Кафедра информатики"),
            ("doc_type", "Тип работы", "ОТЧЁТ"),
            ("subject", "Дисциплина", "Информатика"),
            ("topic", "Тема работы", "Разработка приложения"),
            ("student", "ФИО студента", "Иванов И.И."),
            ("group", "Группа", "ИС-21"),
            ("teacher", "ФИО преподавателя", "Петров П.П."),
            ("city", "Город", "Москва"),
        ]
        self._build_form(f1, title_fields, self.title_inputs)

        ctk.CTkButton(f1, text="📄 Создать и сохранить титульный лист",
                      height=42, font=(FONT_FAMILY, 13, "bold"),
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      corner_radius=10,
                      command=self.create_title).pack(pady=15)

        # ─── Таб 2: Отчёт ───
        f2 = ctk.CTkFrame(tab2, fg_color="transparent")
        f2.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(f2,
                     text="Введи тему — я соберу полный отчёт "
                          "(введение, теория, практика, заключение, источники)",
                     font=(FONT_FAMILY, 12),
                     text_color=TEXT_SECONDARY,
                     wraplength=800, justify="left").pack(anchor="w", pady=(0, 10))

        self.report_inputs = {}
        report_fields = [
            ("topic", "Тема работы (обязательно)", "Искусственный интеллект в образовании"),
            ("subject", "Дисциплина", "Информатика"),
            ("student", "ФИО студента", "Иванов И.И."),
            ("group", "Группа", "ИС-21"),
            ("teacher", "ФИО преподавателя", "Петров П.П."),
        ]
        self._build_form(f2, report_fields, self.report_inputs)

        ctk.CTkButton(f2, text="📝 Создать и сохранить отчёт",
                      height=42, font=(FONT_FAMILY, 13, "bold"),
                      fg_color=SUCCESS, hover_color=ACCENT_HOVER,
                      corner_radius=10,
                      command=self.create_report).pack(pady=15)

        # ─── Кнопки справки ───
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=40, pady=(0, 10))

        ctk.CTkButton(actions, text="📐 Правила ГОСТ", height=36,
                      font=(FONT_FAMILY, 12),
                      fg_color=BG_CARD, hover_color=ACCENT,
                      text_color=TEXT_SECONDARY, corner_radius=10,
                      command=self.show_rules).pack(side="left", padx=4)

        ctk.CTkButton(actions, text="📋 План работы", height=36,
                      font=(FONT_FAMILY, 12),
                      fg_color=BG_CARD, hover_color=ACCENT,
                      text_color=TEXT_SECONDARY, corner_radius=10,
                      command=self.show_outline).pack(side="left", padx=4)

        ctk.CTkButton(actions, text="🧹 Очистить", height=36,
                      font=(FONT_FAMILY, 12),
                      fg_color=BG_CARD, hover_color=ACCENT,
                      text_color=TEXT_SECONDARY, corner_radius=10,
                      command=self.clear_output).pack(side="left", padx=4)

        # ─── Вывод ───
        ctk.CTkLabel(self, text="📋 Информация:",
                     font=(FONT_FAMILY, 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=40, pady=(10, 4))

        self.output = ctk.CTkTextbox(self, font=(FONT_FAMILY, 13),
                                     fg_color=BG_CARD, text_color=TEXT_PRIMARY,
                                     corner_radius=12, wrap="word", border_width=0)
        self.output.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        self.log("👋 Выбери вкладку сверху:\n"
                 "• «📄 Титульный лист» — заполни поля и нажми кнопку\n"
                 "• «📝 Отчёт по теме» — введи тему и получи полный отчёт\n\n"
                 "💾 После генерации откроется окно Windows — выбери, куда сохранить файл.")

    def _build_form(self, parent, fields, storage):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")

        for i, (key, label, placeholder) in enumerate(fields):
            row, col = divmod(i, 2)
            f = ctk.CTkFrame(grid, fg_color="transparent")
            f.grid(row=row, column=col, padx=6, pady=4, sticky="ew")
            grid.grid_columnconfigure(col, weight=1)

            ctk.CTkLabel(f, text=label, font=(FONT_FAMILY, 11),
                         text_color=TEXT_SECONDARY).pack(anchor="w")
            entry = ctk.CTkEntry(f, height=32, font=(FONT_FAMILY, 12),
                                 placeholder_text=placeholder,
                                 fg_color=BG_INPUT, corner_radius=8,
                                 border_width=0)
            entry.pack(fill="x")
            storage[key] = entry

    def log(self, text, clear=False):
        if clear:
            self.output.delete("1.0", "end")
        self.output.insert("end", text + "\n")
        self.output.see("end")

    def clear_output(self):
        self.output.delete("1.0", "end")

    def _collect(self, storage):
        return {k: e.get().strip() for k, e in storage.items() if e.get().strip()}

    def show_rules(self):
        self.log(get_rules(), clear=True)

    def show_outline(self):
        topic = self.report_inputs["topic"].get().strip() or "Тема работы"
        self.log(suggest_outline(topic), clear=True)

    def create_title(self):
        data = self._collect(self.title_inputs)
        try:
            result = generate_title_page(**data)
            self.log(f"\n{result}")
        except Exception as e:
            self.log(f"\n❌ Ошибка: {e}")

    def create_report(self):
        data = self._collect(self.report_inputs)
        topic = data.get("topic", "").strip()
        if not topic:
            self.log("\n⚠️ Укажи тему работы на вкладке «📝 Отчёт по теме».")
            return
        try:
            result = generate_report(**data)
            self.log(f"\n{result}")
        except Exception as e:
            self.log(f"\n❌ Ошибка: {e}")

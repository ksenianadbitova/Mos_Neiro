import customtkinter as ctk
import theme
from logic.physics_templates import get_categories, get_template, calculate
from logic.physics_tutor import list_formulas, find_formula, solve_step_by_step
try:
    from logic.units_converter import convert as unit_convert, get_categories as get_unit_categories, is_available as units_ok
    UNITS_OK = True
except Exception:
    UNITS_OK = False


class PhysicsScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Заголовок
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 6))
        ctk.CTkLabel(header, text="⚛️ Физика: лаборатория",
                     font=(theme.FONT_FAMILY, 26, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Готовые формулы с единицами, решение задач по шагам, конвертация величин",
                     font=(theme.FONT_FAMILY, 12),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        # Вкладки
        self.tabs = ctk.CTkTabview(
            self, fg_color=theme.BG_CARD,
            segmented_button_fg_color=theme.BG_CARD,
            segmented_button_selected_color=theme.ACCENT,
            segmented_button_selected_hover_color=theme.ACCENT_HOVER,
            corner_radius=14,
        )
        self.tabs.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        tab_calc = self.tabs.add("📋 Формулы")
        tab_solve = self.tabs.add("✏️ Задача по шагам")
        tab_units = self.tabs.add("📏 Величины")

        self._build_calc_tab(tab_calc)
        self._build_solve_tab(tab_solve)
        self._build_units_tab(tab_units)

    # ═══════════════════════════════════════════
    # Вкладка 1: Готовые формулы
    # ═══════════════════════════════════════════
    def _build_calc_tab(self, parent):
        ctk.CTkLabel(parent, text="Готовые физические формулы",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(10, 4))
        ctk.CTkLabel(parent, text="Выбери формулу → введи данные → получи результат с единицами",
                     font=(theme.FONT_FAMILY, 12),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(0, 8))

        # Категория
        cats = get_categories()
        cat_names = list(cats.keys())
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(row, text="Раздел:", font=(theme.FONT_FAMILY, 12)).pack(side="left", padx=(0, 6))
        self.cat_menu = ctk.CTkOptionMenu(
            row, values=cat_names, width=240,
            command=self._update_formulas,
        )
        self.cat_menu.pack(side="left")
        self.cat_menu.set(cat_names[0])

        # Формула
        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(row2, text="Формула:", font=(theme.FONT_FAMILY, 12)).pack(side="left", padx=(0, 6))
        self.formula_menu = ctk.CTkOptionMenu(
            row2, values=cats[cat_names[0]], width=400,
            command=self._update_vars,
        )
        self.formula_menu.pack(side="left")

        # Описание формулы
        self.formula_desc = ctk.CTkLabel(parent, text="",
                                          font=(theme.FONT_FAMILY, 13, "bold"),
                                          text_color=theme.ACCENT)
        self.formula_desc.pack(anchor="w", padx=10, pady=(0, 8))

        # Поля ввода
        self.inputs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.inputs_frame.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkButton(parent, text="🧮 Вычислить", height=40, width=180,
                      font=(theme.FONT_FAMILY, 13, "bold"),
                      fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                      corner_radius=10,
                      command=self._calc).pack(anchor="w", padx=10, pady=(0, 8))

        self.calc_result = ctk.CTkTextbox(
            parent, font=(theme.FONT_FAMILY, 14),
            fg_color=theme.BG_INPUT, text_color=theme.TEXT_PRIMARY,
            corner_radius=10, wrap="word", height=140,
        )
        self.calc_result.pack(fill="x", padx=10, pady=(0, 10))

        self.inputs = []
        self._update_formulas(cat_names[0])

    def _update_formulas(self, category):
        cats = get_categories()
        formulas = cats.get(category, [])
        if formulas:
            self.formula_menu.configure(values=formulas)
            self.formula_menu.set(formulas[0])
            self._update_vars(formulas[0])

    def _update_vars(self, name):
        tpl = get_template(name)
        if not tpl:
            return
        self.formula_desc.configure(text=f"📐 {tpl['formula']}   →   результат в: {tpl['unit'] or '—'}")

        for w in self.inputs_frame.winfo_children():
            w.destroy()
        self.inputs = []

        for var in tpl["vars"]:
            row = ctk.CTkFrame(self.inputs_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=var, width=320, anchor="w",
                         font=(theme.FONT_FAMILY, 12),
                         text_color=theme.TEXT_PRIMARY).pack(side="left")
            e = ctk.CTkEntry(row, width=200, height=34,
                             font=(theme.FONT_FAMILY, 13),
                             fg_color=theme.BG_INPUT,
                             corner_radius=6, border_width=0)
            e.pack(side="left", padx=6)
            self.inputs.append(e)

    def _calc(self):
        name = self.formula_menu.get()
        try:
            values = [float(e.get().replace(",", ".")) for e in self.inputs]
        except ValueError:
            self.calc_result.delete("1.0", "end")
            self.calc_result.insert("end", "❌ Все поля должны содержать числа")
            return

        result = calculate(name, values)
        self.calc_result.delete("1.0", "end")
        if result.get("error"):
            self.calc_result.insert("end", f"❌ {result['error']}")
        else:
            self.calc_result.insert("end",
                f"✅ Результат: {result['formatted']}\n\n"
                f"📐 Формула: {result['formula']}\n"
                f"🔢 Значение: {result['result']}\n"
                f"📏 Единица: {result['unit'] or '—'}")

    # ═══════════════════════════════════════════
    # Вкладка 2: Решение задачи по шагам
    # ═══════════════════════════════════════════
    def _build_solve_tab(self, parent):
        ctk.CTkLabel(parent, text="Решение физической задачи по шагам",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(10, 4))
        ctk.CTkLabel(parent, text="Опиши задачу словами — программа разберёт её по шагам и подскажет формулу",
                     font=(theme.FONT_FAMILY, 12),
                     text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(0, 8))

        self.task_input = ctk.CTkTextbox(
            parent, font=(theme.FONT_FAMILY, 13),
            fg_color=theme.BG_INPUT, text_color=theme.TEXT_PRIMARY,
            corner_radius=10, wrap="word", height=120,
        )
        self.task_input.pack(fill="x", padx=10, pady=(0, 8))
        self.task_input.insert("end", "Пример: Поезд прошёл 300 км за 5 часов. Найти скорость.")

        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkButton(btn_row, text="🔍 Разобрать", height=38, width=160,
                      font=(theme.FONT_FAMILY, 13, "bold"),
                      fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                      corner_radius=10,
                      command=self._solve).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="📚 Все формулы", height=38, width=160,
                      font=(theme.FONT_FAMILY, 12),
                      fg_color=theme.BG_CARD, hover_color=theme.ACCENT_LIGHT,
                      text_color=theme.TEXT_SECONDARY, corner_radius=10,
                      border_width=1, border_color=theme.BORDER,
                      command=self._show_all_formulas).pack(side="left")

        self.solve_result = ctk.CTkTextbox(
            parent, font=(theme.FONT_FAMILY, 13),
            fg_color=theme.BG_INPUT, text_color=theme.TEXT_PRIMARY,
            corner_radius=10, wrap="word",
        )
        self.solve_result.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _solve(self):
        task = self.task_input.get("1.0", "end").strip()
        if not task:
            return
        self.solve_result.delete("1.0", "end")
        self.solve_result.insert("end", "🔍 Разбираю задачу...\n\n")
        self.update()

        try:
            result = solve_step_by_step(task)
            self.solve_result.delete("1.0", "end")
            self.solve_result.insert("end", result)
        except Exception as e:
            self.solve_result.insert("end", f"\n❌ Ошибка: {e}")

    def _show_all_formulas(self):
        self.solve_result.delete("1.0", "end")
        try:
            text = list_formulas()
            self.solve_result.insert("end", text)
        except Exception as e:
            self.solve_result.insert("end", f"Ошибка: {e}")

    # ═══════════════════════════════════════════
    # Вкладка 3: Конвертер физических величин
    # ═══════════════════════════════════════════
    def _build_units_tab(self, parent):
        if not UNITS_OK:
            ctk.CTkLabel(parent, text="❌ Модуль конвертации единиц недоступен",
                         font=(theme.FONT_FAMILY, 14), text_color=theme.ERROR).pack(pady=40)
            return

        ctk.CTkLabel(parent, text="Конвертация физических величин",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(10, 6))

        cats = list(get_unit_categories().keys())
        self.unit_cat = ctk.CTkOptionMenu(parent, values=cats, width=240,
                                           command=self._units_update)
        self.unit_cat.pack(anchor="w", padx=10, pady=(0, 8))
        self.unit_cat.set(cats[0])

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 8))

        self.unit_val = ctk.CTkEntry(row, width=140, height=40,
                                      font=(theme.FONT_FAMILY, 14),
                                      placeholder_text="Значение",
                                      fg_color=theme.BG_INPUT,
                                      corner_radius=8, border_width=0)
        self.unit_val.pack(side="left", padx=(0, 6))

        self.unit_from = ctk.CTkOptionMenu(row, values=[""], width=140)
        self.unit_from.pack(side="left", padx=(0, 6))

        ctk.CTkLabel(row, text="→", font=(theme.FONT_FAMILY, 18)).pack(side="left", padx=6)

        self.unit_to = ctk.CTkOptionMenu(row, values=[""], width=140)
        self.unit_to.pack(side="left", padx=(0, 6))

        ctk.CTkButton(row, text="Перевести", width=120, height=40,
                      font=(theme.FONT_FAMILY, 13, "bold"),
                      fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                      corner_radius=10,
                      command=self._units_convert).pack(side="left", padx=(6, 0))

        self.unit_result = ctk.CTkTextbox(
            parent, font=(theme.FONT_FAMILY, 14),
            fg_color=theme.BG_INPUT, text_color=theme.TEXT_PRIMARY,
            corner_radius=10, wrap="word", height=140,
        )
        self.unit_result.pack(fill="x", padx=10, pady=(10, 10))

        self._units_update(cats[0])

    def _units_update(self, category):
        units = get_unit_categories().get(category, [])
        if units:
            self.unit_from.configure(values=units)
            self.unit_to.configure(values=units)
            self.unit_from.set(units[0])
            self.unit_to.set(units[1] if len(units) > 1 else units[0])

    def _units_convert(self):
        try:
            val = float(self.unit_val.get().replace(",", "."))
        except ValueError:
            self.unit_result.delete("1.0", "end")
            self.unit_result.insert("end", "❌ Введите число")
            return
        from_u = self.unit_from.get()
        to_u = self.unit_to.get()
        res = unit_convert(val, from_u, to_u)
        self.unit_result.delete("1.0", "end")
        if res.get("error"):
            self.unit_result.insert("end", f"❌ {res['error']}")
        else:
            self.unit_result.insert("end",
                f"{val} {from_u}  →  {res['formatted']}\n\n"
                f"Точное значение: {res['result']}")

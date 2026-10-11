import customtkinter as ctk
import threading
import math
import theme
from logic.math_tutor import (
    safe_eval, symbolic_simplify, symbolic_expand, symbolic_factor,
    symbolic_solve, symbolic_derivative, symbolic_integral, symbolic_limit,
    symbolic_evaluate, convert_bases, get_plot_data,
)
try:
    from logic.units_converter import convert as unit_convert, get_categories as get_unit_categories, is_available as units_ok
    UNITS_OK = True
except Exception:
    UNITS_OK = False

try:
    from logic.math_templates import get_categories, get_template, calculate as calc_template
    TEMPLATES_OK = True
except Exception:
    TEMPLATES_OK = False


class MathScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Заголовок
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 6))
        ctk.CTkLabel(header, text="🧮 Инженерный расчёт",
                     font=(theme.FONT_FAMILY, 26, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Вычисления, символьная математика, единицы, шаблоны и графики",
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

        tab_calc = self.tabs.add("🔢 Калькулятор")
        tab_symb = self.tabs.add("∞ Символьные")
        tab_units = self.tabs.add("📏 Единицы")
        tab_tpl = self.tabs.add("📋 Шаблоны")
        tab_plot = self.tabs.add("📈 Графики")

        self._build_calc_tab(tab_calc)
        self._build_symbolic_tab(tab_symb)
        self._build_units_tab(tab_units)
        self._build_templates_tab(tab_tpl)
        self._build_plot_tab(tab_plot)

    # ═══════════════════════════════════════════
    # Вкладка 1: Обычный калькулятор
    # ═══════════════════════════════════════════
    def _build_calc_tab(self, parent):
        # Дисплей
        self.calc_display = ctk.CTkEntry(
            parent, height=64, font=(theme.FONT_FAMILY, 24),
            justify="right", fg_color=theme.BG_INPUT,
            corner_radius=12, border_width=0,
            text_color=theme.TEXT_PRIMARY,
        )
        self.calc_display.pack(fill="x", padx=10, pady=(10, 4))

        # Превью
        self.calc_preview = ctk.CTkLabel(
            parent, text="", font=(theme.FONT_FAMILY, 14),
            text_color=theme.TEXT_SECONDARY, anchor="e",
        )
        self.calc_preview.pack(fill="x", padx=14, pady=(0, 6))

        # Сетка кнопок
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for c in range(7):
            grid.grid_columnconfigure(c, weight=1)
        for r in range(6):
            grid.grid_rowconfigure(r, weight=1)

        buttons = [
            # row 0
            ("sin", lambda: self._calc_fn("sin"), theme.ACCENT),
            ("cos", lambda: self._calc_fn("cos"), theme.ACCENT),
            ("tan", lambda: self._calc_fn("tan"), theme.ACCENT),
            ("log", lambda: self._calc_fn("log"), theme.ACCENT),
            ("ln", lambda: self._calc_fn("ln"), theme.ACCENT),
            ("√", lambda: self._calc_insert("sqrt("), theme.ACCENT),
            ("^", lambda: self._calc_insert("^"), theme.ACCENT),
            # row 1
            ("sinh", lambda: self._calc_fn("sinh"), theme.BG_CARD_HOVER),
            ("cosh", lambda: self._calc_fn("cosh"), theme.BG_CARD_HOVER),
            ("tanh", lambda: self._calc_fn("tanh"), theme.BG_CARD_HOVER),
            ("π", lambda: self._calc_insert("pi"), theme.BG_CARD_HOVER),
            ("e", lambda: self._calc_insert("e"), theme.BG_CARD_HOVER),
            ("!", lambda: self._calc_insert("!"), theme.BG_CARD_HOVER),
            ("nCr", lambda: self._calc_insert("nCr("), theme.BG_CARD_HOVER),
            # row 2
            ("7", lambda: self._calc_insert("7"), theme.BG_CARD_HOVER),
            ("8", lambda: self._calc_insert("8"), theme.BG_CARD_HOVER),
            ("9", lambda: self._calc_insert("9"), theme.BG_CARD_HOVER),
            ("÷", lambda: self._calc_insert("/"), theme.BG_CARD_HOVER),
            ("×", lambda: self._calc_insert("*"), theme.BG_CARD_HOVER),
            ("C", self._calc_clear, "#E23B3B"),
            ("⌫", self._calc_backspace, "#E68A00"),
            # row 3
            ("4", lambda: self._calc_insert("4"), theme.BG_CARD_HOVER),
            ("5", lambda: self._calc_insert("5"), theme.BG_CARD_HOVER),
            ("6", lambda: self._calc_insert("6"), theme.BG_CARD_HOVER),
            ("−", lambda: self._calc_insert("-"), theme.BG_CARD_HOVER),
            ("+", lambda: self._calc_insert("+"), theme.BG_CARD_HOVER),
            ("(", lambda: self._calc_insert("("), theme.BG_CARD_HOVER),
            (")", lambda: self._calc_insert(")"), theme.BG_CARD_HOVER),
            # row 4
            ("1", lambda: self._calc_insert("1"), theme.BG_CARD_HOVER),
            ("2", lambda: self._calc_insert("2"), theme.BG_CARD_HOVER),
            ("3", lambda: self._calc_insert("3"), theme.BG_CARD_HOVER),
            ("0", lambda: self._calc_insert("0"), theme.BG_CARD_HOVER),
            (".", lambda: self._calc_insert("."), theme.BG_CARD_HOVER),
            ("gcd", lambda: self._calc_insert("gcd("), theme.BG_CARD_HOVER),
            ("lcm", lambda: self._calc_insert("lcm("), theme.BG_CARD_HOVER),
            # row 5
            ("asin", lambda: self._calc_fn("asin"), theme.ACCENT),
            ("acos", lambda: self._calc_fn("acos"), theme.ACCENT),
            ("atan", lambda: self._calc_fn("atan"), theme.ACCENT),
            ("abs", lambda: self._calc_insert("abs("), theme.ACCENT),
            ("rad", lambda: self._calc_insert("radians("), theme.ACCENT),
            ("=", self._calc_calculate, "#22A06B"),
            ("→bin", self._calc_to_base, theme.BG_CARD_HOVER),
        ]

        for i, (label, cmd, color) in enumerate(buttons):
            r, c = divmod(i, 7)
            b = ctk.CTkButton(
                grid, text=label,
                font=(theme.FONT_FAMILY, 14, "bold"),
                fg_color=color, hover_color=theme.ACCENT_HOVER,
                text_color="#FFFFFF", corner_radius=8,
                command=cmd,
            )
            b.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

        self.calc_display.bind("<Return>", lambda e: self._calc_calculate())

    def _calc_insert(self, text):
        cur = self.calc_display.get()
        self.calc_display.delete(0, "end")
        self.calc_display.insert(0, cur + text)
        self._calc_update_preview()

    def _calc_fn(self, name):
        self._calc_insert(f"{name}(")

    def _calc_clear(self):
        self.calc_display.delete(0, "end")
        self.calc_preview.configure(text="")

    def _calc_backspace(self):
        cur = self.calc_display.get()
        self.calc_display.delete(0, "end")
        self.calc_display.insert(0, cur[:-1])
        self._calc_update_preview()

    def _calc_update_preview(self):
        expr = self.calc_display.get().strip()
        if not expr:
            self.calc_preview.configure(text="")
            return
        try:
            r = safe_eval(expr)
            self.calc_preview.configure(text=f"= {r:.10g}")
        except Exception:
            self.calc_preview.configure(text="")

    def _calc_calculate(self):
        expr = self.calc_display.get().strip()
        if not expr:
            return
        try:
            result = safe_eval(expr)
            self.calc_display.delete(0, "end")
            self.calc_display.insert(0, str(result))
            self.calc_preview.configure(text="")
        except ZeroDivisionError:
            self.calc_display.delete(0, "end")
            self.calc_display.insert(0, "Деление на ноль!")
        except Exception as e:
            self.calc_display.delete(0, "end")
            self.calc_display.insert(0, f"Ошибка: {e}")

    def _calc_to_base(self):
        """Показывает число в bin/oct/hex."""
        try:
            n = int(safe_eval(self.calc_display.get()))
            bases = convert_bases(str(n), 10)
            self.calc_preview.configure(
                text=f"HEX: {bases['hex']}  |  OCT: {bases['oct']}  |  BIN: {bases['bin']}"
            )
        except Exception as e:
            self.calc_preview.configure(text=f"Ошибка: {e}")

    # ═══════════════════════════════════════════
    # Вкладка 2: Символьные вычисления
    # ═══════════════════════════════════════════
    def _build_symbolic_tab(self, parent):
        ctk.CTkLabel(parent, text="Символьные вычисления (SymPy)",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(10, 6))

        self.symb_input = ctk.CTkEntry(
            parent, height=44, font=(theme.FONT_FAMILY, 14),
            placeholder_text="Введи выражение: x^2 - 4 или 2x + 3 = 7",
            fg_color=theme.BG_INPUT, corner_radius=10, border_width=0,
        )
        self.symb_input.pack(fill="x", padx=10, pady=(0, 10))

        btns = ctk.CTkFrame(parent, fg_color="transparent")
        btns.pack(fill="x", padx=10, pady=(0, 10))

        actions = [
            ("Упростить", lambda: self._symb_action(symbolic_simplify)),
            ("Раскрыть", lambda: self._symb_action(symbolic_expand)),
            ("Разложить", lambda: self._symb_action(symbolic_factor)),
            ("Решить = 0", lambda: self._symb_action(symbolic_solve)),
            ("Производная", lambda: self._symb_action(symbolic_derivative)),
            ("Интеграл", lambda: self._symb_action(symbolic_integral)),
        ]
        for text, cmd in actions:
            ctk.CTkButton(btns, text=text, height=34, width=110,
                          font=(theme.FONT_FAMILY, 12),
                          fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                          corner_radius=8, command=cmd).pack(side="left", padx=3)

        self.symb_output = ctk.CTkTextbox(
            parent, font=(theme.FONT_FAMILY, 14),
            fg_color=theme.BG_INPUT, text_color=theme.TEXT_PRIMARY,
            corner_radius=10, wrap="word",
        )
        self.symb_output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _symb_action(self, func):
        expr = self.symb_input.get().strip()
        if not expr:
            return
        try:
            result = func(expr)
        except Exception as e:
            result = f"Ошибка: {e}"
        self.symb_output.delete("1.0", "end")
        self.symb_output.insert("end", f"Вход:  {expr}\n\nРезультат:\n  {result}")

    # ═══════════════════════════════════════════
    # Вкладка 3: Конвертер единиц
    # ═══════════════════════════════════════════
    def _build_units_tab(self, parent):
        if not UNITS_OK:
            ctk.CTkLabel(parent, text="❌ Модуль конвертации единиц недоступен",
                         font=(theme.FONT_FAMILY, 14), text_color=theme.ERROR).pack(pady=40)
            return

        ctk.CTkLabel(parent, text="Конвертация единиц измерения (pint)",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(10, 6))

        # Категория
        cats = list(get_unit_categories().keys())
        self.unit_category = ctk.CTkOptionMenu(
            parent, values=cats, width=200,
            command=self._units_update_units,
        )
        self.unit_category.pack(anchor="w", padx=10, pady=(0, 8))
        self.unit_category.set(cats[0])

        # Строка ввода
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 8))

        self.unit_value = ctk.CTkEntry(row, width=140, height=40,
                                       font=(theme.FONT_FAMILY, 14),
                                       placeholder_text="Значение",
                                       fg_color=theme.BG_INPUT,
                                       corner_radius=8, border_width=0)
        self.unit_value.pack(side="left", padx=(0, 6))

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
            corner_radius=10, wrap="word", height=120,
        )
        self.unit_result.pack(fill="x", padx=10, pady=(10, 10))

        self._units_update_units(cats[0])

    def _units_update_units(self, category):
        units = get_unit_categories().get(category, [])
        if units:
            self.unit_from.configure(values=units)
            self.unit_to.configure(values=units)
            self.unit_from.set(units[0])
            self.unit_to.set(units[1] if len(units) > 1 else units[0])

    def _units_convert(self):
        try:
            val = float(self.unit_value.get().replace(",", "."))
        except ValueError:
            self.unit_result.delete("1.0", "end")
            self.unit_result.insert("end", "❌ Введите число")
            return

        from_unit = self.unit_from.get()
        to_unit = self.unit_to.get()
        result = unit_convert(val, from_unit, to_unit)

        self.unit_result.delete("1.0", "end")
        if result.get("error"):
            self.unit_result.insert("end", f"❌ {result['error']}")
        else:
            self.unit_result.insert("end",
                f"{val} {from_unit}  →  {result['formatted']}\n\n"
                f"Точное значение: {result['result']}")

    # ═══════════════════════════════════════════
    # Вкладка 4: Инженерные шаблоны
    # ═══════════════════════════════════════════
    def _build_templates_tab(self, parent):
        if not TEMPLATES_OK:
            ctk.CTkLabel(parent, text="❌ Шаблоны недоступны",
                         font=(theme.FONT_FAMILY, 14), text_color=theme.ERROR).pack(pady=40)
            return

        ctk.CTkLabel(parent, text="Готовые инженерные формулы",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(10, 6))

        cats = get_categories()
        all_names = []
        for cat, names in cats.items():
            all_names.extend(names)

        self.tpl_choice = ctk.CTkOptionMenu(
            parent, values=all_names, width=400,
            command=self._tpl_update,
        )
        self.tpl_choice.pack(anchor="w", padx=10, pady=(0, 8))

        self.tpl_desc = ctk.CTkLabel(
            parent, text="", font=(theme.FONT_FAMILY, 13),
            text_color=theme.TEXT_SECONDARY, justify="left",
        )
        self.tpl_desc.pack(anchor="w", padx=10, pady=(0, 8))

        self.tpl_inputs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.tpl_inputs_frame.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkButton(parent, text="Вычислить", height=40,
                      font=(theme.FONT_FAMILY, 13, "bold"),
                      fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                      corner_radius=10,
                      command=self._tpl_calc).pack(anchor="w", padx=10, pady=(0, 8))

        self.tpl_result = ctk.CTkTextbox(
            parent, font=(theme.FONT_FAMILY, 14),
            fg_color=theme.BG_INPUT, text_color=theme.TEXT_PRIMARY,
            corner_radius=10, wrap="word", height=140,
        )
        self.tpl_result.pack(fill="x", padx=10, pady=(0, 10))

        self.tpl_inputs = []
        self._tpl_update(all_names[0])

    def _tpl_update(self, name):
        tpl = get_template(name)
        if not tpl:
            return
        self.tpl_desc.configure(text=f"Формула: {tpl['formula']}\nРезультат в: {tpl['unit'] or '—'}")

        for w in self.tpl_inputs_frame.winfo_children():
            w.destroy()
        self.tpl_inputs = []

        for var in tpl["vars"]:
            row = ctk.CTkFrame(self.tpl_inputs_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=var, width=300, anchor="w",
                         font=(theme.FONT_FAMILY, 12),
                         text_color=theme.TEXT_PRIMARY).pack(side="left")
            e = ctk.CTkEntry(row, width=200, height=34,
                             font=(theme.FONT_FAMILY, 12),
                             fg_color=theme.BG_INPUT,
                             corner_radius=6, border_width=0)
            e.pack(side="left", padx=6)
            self.tpl_inputs.append(e)

    def _tpl_calc(self):
        name = self.tpl_choice.get()
        try:
            values = [float(e.get().replace(",", ".")) for e in self.tpl_inputs]
        except ValueError:
            self.tpl_result.delete("1.0", "end")
            self.tpl_result.insert("end", "❌ Все поля должны содержать числа")
            return

        result = calc_template(name, values)
        self.tpl_result.delete("1.0", "end")
        if result.get("error"):
            self.tpl_result.insert("end", f"❌ {result['error']}")
        else:
            self.tpl_result.insert("end",
                f"✅ Результат: {result['formatted']}\n\n"
                f"Формула: {result['formula']}\n"
                f"Значение: {result['result']}")

    # ═══════════════════════════════════════════
    # Вкладка 5: Графики
    # ═══════════════════════════════════════════
    def _build_plot_tab(self, parent):
        ctk.CTkLabel(parent, text="Построение графиков функций",
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(10, 6))

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(row, text="f(x) =", font=(theme.FONT_FAMILY, 13)).pack(side="left", padx=(0, 6))
        self.plot_input = ctk.CTkEntry(row, height=40, font=(theme.FONT_FAMILY, 14),
                                       placeholder_text="sin(x) + x^2/10",
                                       fg_color=theme.BG_INPUT,
                                       corner_radius=8, border_width=0)
        self.plot_input.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(row, text="Построить", width=120, height=40,
                      font=(theme.FONT_FAMILY, 13, "bold"),
                      fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                      corner_radius=10,
                      command=self._plot_draw).pack(side="left")

        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(row2, text="X от", font=(theme.FONT_FAMILY, 12)).pack(side="left")
        self.plot_xmin = ctk.CTkEntry(row2, width=80, height=32, font=(theme.FONT_FAMILY, 12))
        self.plot_xmin.insert(0, "-10")
        self.plot_xmin.pack(side="left", padx=4)
        ctk.CTkLabel(row2, text="до", font=(theme.FONT_FAMILY, 12)).pack(side="left")
        self.plot_xmax = ctk.CTkEntry(row2, width=80, height=32, font=(theme.FONT_FAMILY, 12))
        self.plot_xmax.insert(0, "10")
        self.plot_xmax.pack(side="left", padx=4)

        # Область для графика
        self.plot_frame = ctk.CTkFrame(parent, fg_color=theme.BG_INPUT,
                                        corner_radius=10)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.plot_status = ctk.CTkLabel(self.plot_frame, text="Введи функцию и нажми «Построить»",
                                         font=(theme.FONT_FAMILY, 13),
                                         text_color=theme.TEXT_SECONDARY)
        self.plot_status.pack(expand=True, pady=20)

    def _plot_draw(self):
        expr = self.plot_input.get().strip()
        if not expr:
            return
        try:
            xmin = float(self.plot_xmin.get())
            xmax = float(self.plot_xmax.get())
        except ValueError:
            xmin, xmax = -10, 10

        data = get_plot_data(expr, "x", xmin, xmax)
        if data.get("error"):
            self.plot_status.configure(text=f"❌ {data['error']}")
            return
        if not data["x"]:
            self.plot_status.configure(text="❌ Не удалось построить график")
            return

        # Строим через matplotlib
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig, ax = plt.subplots(figsize=(8, 4), dpi=80)
            ax.plot(data["x"], data["y"], color="#6C5CE7", linewidth=2)
            ax.axhline(0, color="#888", linewidth=0.5)
            ax.axvline(0, color="#888", linewidth=0.5)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.set_title(f"f(x) = {expr}")
            fig.tight_layout()

            # Очищаем фрейм
            for w in self.plot_frame.winfo_children():
                w.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        except Exception as e:
            self.plot_status.configure(text=f"❌ Ошибка отрисовки: {e}")

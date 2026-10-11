"""
Физические шаблоны: кинематика, динамика, термодинамика, электричество, оптика, колебания.
Каждая формула — с единицами измерения.
"""
import math


G = 9.81  # ускорение свободного падения


TEMPLATES = {
    # ═══ КИНЕМАТИКА ═══
    "Скорость (равномерное движение)": {
        "formula": "v = S / t",
        "vars": ["S (путь, м)", "t (время, с)"],
        "calc": "v = S / t",
        "unit": "м/с",
        "category": "🏃 Кинематика",
    },
    "Путь (равномерное движение)": {
        "formula": "S = v × t",
        "vars": ["v (скорость, м/с)", "t (время, с)"],
        "calc": "S = v * t",
        "unit": "м",
        "category": "🏃 Кинематика",
    },
    "Ускорение": {
        "formula": "a = (v − v₀) / t",
        "vars": ["v (конечная скорость, м/с)", "v₀ (начальная скорость, м/с)", "t (время, с)"],
        "calc": "a = (v - v0) / t",
        "unit": "м/с²",
        "category": "🏃 Кинематика",
    },
    "Путь при равноускоренном движении": {
        "formula": "S = v₀ × t + a × t² / 2",
        "vars": ["v₀ (начальная скорость, м/с)", "t (время, с)", "a (ускорение, м/с²)"],
        "calc": "S = v0 * t + a * t**2 / 2",
        "unit": "м",
        "category": "🏃 Кинематика",
    },
    "Свободное падение (высота)": {
        "formula": "h = g × t² / 2",
        "vars": ["t (время, с)"],
        "calc": f"h = {G} * t**2 / 2",
        "unit": "м",
        "category": "🏃 Кинематика",
    },
    "Свободное падение (скорость)": {
        "formula": "v = g × t",
        "vars": ["t (время, с)"],
        "calc": f"v = {G} * t",
        "unit": "м/с",
        "category": "🏃 Кинематика",
    },

    # ═══ ДИНАМИКА ═══
    "Второй закон Ньютона": {
        "formula": "F = m × a",
        "vars": ["m (масса, кг)", "a (ускорение, м/с²)"],
        "calc": "F = m * a",
        "unit": "Н",
        "category": "💪 Динамика",
    },
    "Вес тела": {
        "formula": "P = m × g",
        "vars": ["m (масса, кг)"],
        "calc": f"P = m * {G}",
        "unit": "Н",
        "category": "💪 Динамика",
    },
    "Импульс тела": {
        "formula": "p = m × v",
        "vars": ["m (масса, кг)", "v (скорость, м/с)"],
        "calc": "p = m * v",
        "unit": "кг·м/с",
        "category": "💪 Динамика",
    },
    "Кинетическая энергия": {
        "formula": "Eₖ = m × v² / 2",
        "vars": ["m (масса, кг)", "v (скорость, м/с)"],
        "calc": "E = m * v**2 / 2",
        "unit": "Дж",
        "category": "💪 Динамика",
    },
    "Потенциальная энергия": {
        "formula": "Eₚ = m × g × h",
        "vars": ["m (масса, кг)", "h (высота, м)"],
        "calc": f"E = m * {G} * h",
        "unit": "Дж",
        "category": "💪 Динамика",
    },
    "Работа": {
        "formula": "A = F × S",
        "vars": ["F (сила, Н)", "S (перемещение, м)"],
        "calc": "A = F * S",
        "unit": "Дж",
        "category": "💪 Динамика",
    },
    "Мощность": {
        "formula": "N = A / t",
        "vars": ["A (работа, Дж)", "t (время, с)"],
        "calc": "N = A / t",
        "unit": "Вт",
        "category": "💪 Динамика",
    },
    "Момент силы": {
        "formula": "M = F × l",
        "vars": ["F (сила, Н)", "l (плечо, м)"],
        "calc": "M = F * l",
        "unit": "Н·м",
        "category": "💪 Динамика",
    },
    "Сила трения": {
        "formula": "F = μ × N",
        "vars": ["μ (коэф. трения)", "N (сила реакции, Н)"],
        "calc": "F = mu * N",
        "unit": "Н",
        "category": "💪 Динамика",
    },

    # ═══ ТЕРМОДИНАМИКА ═══
    "Количество теплоты (нагревание)": {
        "formula": "Q = c × m × ΔT",
        "vars": ["c (уд. теплоёмкость, Дж/(кг·°C))", "m (масса, кг)", "ΔT (разность T, °C)"],
        "calc": "Q = c * m * dT",
        "unit": "Дж",
        "category": "🔥 Термодинамика",
    },
    "Уравнение Менделеева-Клапейрона": {
        "formula": "P × V = ν × R × T",
        "vars": ["ν (кол-во вещества, моль)", "T (температура, К)"],
        "calc": "PV = nu * 8.314 * T",
        "unit": "Дж",
        "category": "🔥 Термодинамика",
    },
    "Давление идеального газа": {
        "formula": "P = n × k × T",
        "vars": ["n (концентрация, 1/м³)", "T (температура, К)"],
        "calc": "P = n * 1.38e-23 * T",
        "unit": "Па",
        "category": "🔥 Термодинамика",
    },
    "КПД тепловой машины": {
        "formula": "η = (Q₁ − Q₂) / Q₁ × 100%",
        "vars": ["Q₁ (нагреватель, Дж)", "Q₂ (холодильник, Дж)"],
        "calc": "eta = (Q1 - Q2) / Q1 * 100",
        "unit": "%",
        "category": "🔥 Термодинамика",
    },

    # ═══ ЭЛЕКТРИЧЕСТВО ═══
    "Закон Ома (ток)": {
        "formula": "I = U / R",
        "vars": ["U (напряжение, В)", "R (сопротивление, Ом)"],
        "calc": "I = U / R",
        "unit": "А",
        "category": "⚡ Электричество",
    },
    "Закон Ома (напряжение)": {
        "formula": "U = I × R",
        "vars": ["I (ток, А)", "R (сопротивление, Ом)"],
        "calc": "U = I * R",
        "unit": "В",
        "category": "⚡ Электричество",
    },
    "Закон Ома (сопротивление)": {
        "formula": "R = U / I",
        "vars": ["U (напряжение, В)", "I (ток, А)"],
        "calc": "R = U / I",
        "unit": "Ом",
        "category": "⚡ Электричество",
    },
    "Мощность тока": {
        "formula": "P = U × I",
        "vars": ["U (напряжение, В)", "I (ток, А)"],
        "calc": "P = U * I",
        "unit": "Вт",
        "category": "⚡ Электричество",
    },
    "Закон Джоуля-Ленца": {
        "formula": "Q = I² × R × t",
        "vars": ["I (ток, А)", "R (Ом)", "t (время, с)"],
        "calc": "Q = I**2 * R * t",
        "unit": "Дж",
        "category": "⚡ Электричество",
    },
    "Последовательное соединение": {
        "formula": "R = R₁ + R₂",
        "vars": ["R₁ (Ом)", "R₂ (Ом)"],
        "calc": "R = R1 + R2",
        "unit": "Ом",
        "category": "⚡ Электричество",
    },
    "Параллельное соединение": {
        "formula": "R = R₁ × R₂ / (R₁ + R₂)",
        "vars": ["R₁ (Ом)", "R₂ (Ом)"],
        "calc": "R = R1 * R2 / (R1 + R2)",
        "unit": "Ом",
        "category": "⚡ Электричество",
    },
    "Ёмкость конденсатора": {
        "formula": "C = q / U",
        "vars": ["q (заряд, Кл)", "U (напряжение, В)"],
        "calc": "C = q / U",
        "unit": "Ф",
        "category": "⚡ Электричество",
    },

    # ═══ ОПТИКА ═══
    "Тонкая линза": {
        "formula": "1/F = 1/d + 1/f",
        "vars": ["d (расстояние до предмета, м)", "f (расстояние до изображения, м)"],
        "calc": "F = 1 / (1/d + 1/f)",
        "unit": "м",
        "category": "🔍 Оптика",
    },
    "Оптическая сила линзы": {
        "formula": "D = 1 / F",
        "vars": ["F (фокусное расстояние, м)"],
        "calc": "D = 1 / F",
        "unit": "дптр",
        "category": "🔍 Оптика",
    },
    "Закон отражения (угол)": {
        "formula": "β = α",
        "vars": ["α (угол падения, °)"],
        "calc": "beta = alpha",
        "unit": "°",
        "category": "🔍 Оптика",
    },

    # ═══ КОЛЕБАНИЯ И ВОЛНЫ ═══
    "Период математического маятника": {
        "formula": "T = 2π√(L / g)",
        "vars": ["L (длина нити, м)"],
        "calc": f"T = 2 * 3.141592653589793 * math.sqrt(L / {G})",
        "unit": "с",
        "category": "🌊 Колебания",
    },
    "Период пружинного маятника": {
        "formula": "T = 2π√(m / k)",
        "vars": ["m (масса, кг)", "k (жёсткость, Н/м)"],
        "calc": "T = 2 * 3.141592653589793 * math.sqrt(m / k)",
        "unit": "с",
        "category": "🌊 Колебания",
    },
    "Частота колебаний": {
        "formula": "ν = 1 / T",
        "vars": ["T (период, с)"],
        "calc": "nu = 1 / T",
        "unit": "Гц",
        "category": "🌊 Колебания",
    },
    "Скорость волны": {
        "formula": "v = λ × ν",
        "vars": ["λ (длина волны, м)", "ν (частота, Гц)"],
        "calc": "v = lam * nu",
        "unit": "м/с",
        "category": "🌊 Колебания",
    },
}


def get_categories() -> dict:
    result = {}
    for name, tpl in TEMPLATES.items():
        cat = tpl["category"]
        if cat not in result:
            result[cat] = []
        result[cat].append(name)
    return result


def get_template(name: str) -> dict:
    return TEMPLATES.get(name)


def calculate(name: str, values: list) -> dict:
    tpl = TEMPLATES.get(name)
    if not tpl:
        return {"error": f"Шаблон «{name}» не найден"}
    if len(values) != len(tpl["vars"]):
        return {"error": f"Ожидалось {len(tpl['vars'])} значений, получено {len(values)}"}

    import re
    var_names = []
    for v in tpl["vars"]:
        m = re.match(r"([A-Za-zа-яА-ЯёЁ0-9₀₁₂ᵢ]+)", v)
        var_names.append(m.group(1) if m else v)

    # Заменяем индексы на ASCII
    clean_names = []
    for n in var_names:
        n = (n.replace("₀", "0").replace("₁", "1").replace("₂", "2")
              .replace("₃", "3").replace("ₙ", "n"))
        clean_names.append(n)

    local_vars = dict(zip(clean_names, values))

    # Дополнительные алиасы
    for i, n in enumerate(clean_names):
        local_vars[n] = values[i]
        # Если имя содержит русские буквы — создаём транслит
        if n in ("ΔT", "dT") and i < len(values):
            local_vars["dT"] = values[i]
        if n == "ν" or n == "nu":
            local_vars["nu"] = values[i]
        if n == "λ" or n == "lam":
            local_vars["lam"] = values[i]
        if n == "μ" or n == "mu":
            local_vars["mu"] = values[i]
        if n == "η" or n == "eta":
            local_vars["eta"] = values[i]

    # Фиксим часто встречающиеся имена
    if "v₀" in "".join(var_names):
        local_vars["v0"] = values[0]
    if "Q₁" in "".join(var_names):
        local_vars["Q1"] = values[0]
        local_vars["Q2"] = values[1]

    try:
        expr = tpl["calc"].split("=", 1)[1].strip()
        result = eval(expr, {"__builtins__": {}, "math": math}, local_vars)
        return {
            "result": result,
            "formula": tpl["formula"],
            "unit": tpl["unit"],
            "formatted": f"{result:.6g} {tpl['unit']}".strip(),
            "error": None,
        }
    except Exception as e:
        return {"error": f"Ошибка расчёта: {e}"}

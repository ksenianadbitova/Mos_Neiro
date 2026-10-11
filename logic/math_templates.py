"""
Математические шаблоны: геометрия, алгебра, статистика, проценты.
БЕЗ ФИЗИКИ — физика в отдельном модуле physics_templates.py
"""
import math


TEMPLATES = {
    # Геометрия — площадь
    "Площадь круга": {
        "formula": "S = π × R²",
        "vars": ["R (радиус)"],
        "calc": "S = 3.141592653589793 * R**2",
        "unit": "кв. ед.",
        "category": "📐 Геометрия",
    },
    "Площадь треугольника (по основанию и высоте)": {
        "formula": "S = ½ × a × h",
        "vars": ["a (основание)", "h (высота)"],
        "calc": "S = 0.5 * a * h",
        "unit": "кв. ед.",
        "category": "📐 Геометрия",
    },
    "Площадь прямоугольника": {
        "formula": "S = a × b",
        "vars": ["a (длина)", "b (ширина)"],
        "calc": "S = a * b",
        "unit": "кв. ед.",
        "category": "📐 Геометрия",
    },
    "Площадь трапеции": {
        "formula": "S = (a + b) / 2 × h",
        "vars": ["a (основание 1)", "b (основание 2)", "h (высота)"],
        "calc": "S = (a + b) / 2 * h",
        "unit": "кв. ед.",
        "category": "📐 Геометрия",
    },

    # Геометрия — объём
    "Объём шара": {
        "formula": "V = 4/3 × π × R³",
        "vars": ["R (радиус)"],
        "calc": "V = 4/3 * 3.141592653589793 * R**3",
        "unit": "куб. ед.",
        "category": "📐 Геометрия",
    },
    "Объём цилиндра": {
        "formula": "V = π × R² × h",
        "vars": ["R (радиус)", "h (высота)"],
        "calc": "V = 3.141592653589793 * R**2 * h",
        "unit": "куб. ед.",
        "category": "📐 Геометрия",
    },
    "Объём конуса": {
        "formula": "V = 1/3 × π × R² × h",
        "vars": ["R (радиус)", "h (высота)"],
        "calc": "V = 1/3 * 3.141592653589793 * R**2 * h",
        "unit": "куб. ед.",
        "category": "📐 Геометрия",
    },
    "Объём параллелепипеда": {
        "formula": "V = a × b × c",
        "vars": ["a", "b", "c"],
        "calc": "V = a * b * c",
        "unit": "куб. ед.",
        "category": "📐 Геометрия",
    },

    # Геометрия — теоремы
    "Теорема Пифагора (гипотенуза)": {
        "formula": "c = √(a² + b²)",
        "vars": ["a (катет)", "b (катет)"],
        "calc": "c = (a**2 + b**2) ** 0.5",
        "unit": "",
        "category": "📐 Геометрия",
    },
    "Теорема Пифагора (катет)": {
        "formula": "a = √(c² − b²)",
        "vars": ["c (гипотенуза)", "b (катет)"],
        "calc": "a = (c**2 - b**2) ** 0.5",
        "unit": "",
        "category": "📐 Геометрия",
    },

    # Алгебра
    "Корни квадратного уравнения": {
        "formula": "x = (−b ± √D) / (2a), D = b² − 4ac",
        "vars": ["a", "b", "c"],
        "calc": "D = b**2 - 4*a*c",
        "unit": "",
        "category": "🔢 Алгебра",
        "extra": "D",
    },
    "Сумма арифметической прогрессии": {
        "formula": "S = (a₁ + aₙ) × n / 2",
        "vars": ["a₁ (первый член)", "aₙ (последний член)", "n (кол-во)"],
        "calc": "S = (a1 + an) * n / 2",
        "unit": "",
        "category": "🔢 Алгебра",
    },
    "Сумма геометрической прогрессии": {
        "formula": "S = b₁ × (qⁿ − 1) / (q − 1)",
        "vars": ["b₁ (первый член)", "q (знаменатель)", "n (кол-во)"],
        "calc": "S = b1 * (q**n - 1) / (q - 1)",
        "unit": "",
        "category": "🔢 Алгебра",
    },

    # Проценты и финансы
    "Процент от числа": {
        "formula": "результат = число × процент / 100",
        "vars": ["число", "процент"],
        "calc": "r = number * percent / 100",
        "unit": "",
        "category": "💰 Проценты",
    },
    "Сложный процент": {
        "formula": "S = P × (1 + r/100)ⁿ",
        "vars": ["P (начальная сумма)", "r (процент годовых)", "n (лет)"],
        "calc": "S = P * (1 + r/100) ** n",
        "unit": "",
        "category": "💰 Проценты",
    },

    # Статистика
    "Среднее арифметическое": {
        "formula": "x̄ = (x₁ + x₂ + ... + xₙ) / n",
        "vars": ["сумма", "количество"],
        "calc": "x = s / n",
        "unit": "",
        "category": "📊 Статистика",
    },
    "Дисперсия выборки": {
        "formula": "D = Σ(xᵢ − x̄)² / n",
        "vars": ["сумма квадратов отклонений", "количество"],
        "calc": "D = s / n",
        "unit": "",
        "category": "📊 Статистика",
    },
}


def get_categories() -> dict:
    """Возвращает шаблоны, сгруппированные по категориям."""
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
    """Выполняет расчёт по шаблону."""
    tpl = TEMPLATES.get(name)
    if not tpl:
        return {"error": f"Шаблон «{name}» не найден"}
    if len(values) != len(tpl["vars"]):
        return {"error": f"Ожидалось {len(tpl['vars'])} значений, получено {len(values)}"}

    import re
    var_names = []
    for v in tpl["vars"]:
        m = re.match(r"([A-Za-zа-яА-ЯёЁ0-9₁₂ₙ]+)", v)
        var_names.append(m.group(1) if m else v)

    local_vars = dict(zip(var_names, values))

    # Алиасы для переменных с индексами
    if len(values) >= 3:
        local_vars["a1"] = values[0]
        local_vars["an"] = values[1]
        local_vars["b1"] = values[0]
        local_vars["q"] = values[1]
    if len(values) >= 2:
        local_vars["number"] = values[0]
        local_vars["percent"] = values[1]
        local_vars["P"] = values[0]
        local_vars["r"] = values[1]
        local_vars["s"] = values[0]
        local_vars["n"] = values[1] if len(values) > 1 else 1

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

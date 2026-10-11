"""
Инженерный математический движок.
- Безопасное вычисление выражений (ast)
- Продвинутые функции (гиперболические, комбинаторика, теория чисел)
- Символьные вычисления через sympy
- Системы счисления
"""
import math
import ast
import operator as op
import re

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application,
)


# ─────────────────────────────────────────────
# Безопасные операции
# ─────────────────────────────────────────────
SAFE_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
    ast.USub: op.neg, ast.UAdd: op.pos,
    ast.FloorDiv: op.floordiv,
}

# Все функции, доступные в калькуляторе
SAFE_FUNCS = {
    # Тригонометрия (градусы)
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    # Обратная тригонометрия (возвращает градусы)
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    # Гиперболические
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "asinh": math.asinh,
    "acosh": math.acosh,
    "atanh": math.atanh,
    # Логарифмы
    "log": math.log10,
    "ln": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    # Корни и степени
    "sqrt": math.sqrt,
    "cbrt": lambda x: x ** (1/3) if x >= 0 else -((-x) ** (1/3)),
    "pow": lambda x, y: x ** y,
    # Модуль и округление
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    # Комбинаторика
    "fact": math.factorial,
    "factorial": math.factorial,
    "nCr": lambda n, r: math.comb(int(n), int(r)),
    "nPr": lambda n, r: math.perm(int(n), int(r)),
    "comb": lambda n, r: math.comb(int(n), int(r)),
    "perm": lambda n, r: math.perm(int(n), int(r)),
    "gcd": math.gcd,
    "lcm": math.lcm,
    # Прочее
    "radians": math.radians,
    "degrees": math.degrees,
    "min": min,
    "max": max,
    "sum": sum,
}

SAFE_CONSTS = {
    "pi": math.pi,
    "π": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    "phi": (1 + math.sqrt(5)) / 2,  # золотое сечение
}


# ─────────────────────────────────────────────
# Функция безопасного вычисления
# ─────────────────────────────────────────────
def _preprocess(expr: str) -> str:
    """Заменяет пользовательские обозначения на Python-совместимые."""
    expr = expr.replace("^", "**")
    expr = expr.replace("√", "sqrt")
    expr = expr.replace("×", "*")
    expr = expr.replace("÷", "/")
    expr = expr.replace("−", "-")
    expr = expr.replace("π", "pi")
    # Комбинаторика: "5!" → "fact(5)", "10!/(3!*7!)" → корректно
    expr = re.sub(r"(\d+(?:\.\d+)?)!", r"fact(\1)", expr)
    return expr


def safe_eval(expr: str):
    """Безопасно вычисляет выражение, возвращает число или строку с ошибкой."""
    if not expr or not expr.strip():
        raise ValueError("Пустое выражение")

    expr = _preprocess(expr)
    tree = ast.parse(expr, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPS:
                raise ValueError(f"Операция не поддерживается")
            return SAFE_OPS[op_type](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPS:
                raise ValueError("Унарная операция не поддерживается")
            return SAFE_OPS[op_type](_eval(node.operand))
        if isinstance(node, ast.Name):
            if node.id in SAFE_CONSTS:
                return SAFE_CONSTS[node.id]
            raise ValueError(f"Неизвестная переменная: {node.id}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Сложные вызовы не поддерживаются")
            name = node.func.id
            if name not in SAFE_FUNCS:
                raise ValueError(f"Неизвестная функция: {name}")
            args = [_eval(a) for a in node.args]
            return SAFE_FUNCS[name](*args)
        raise ValueError(f"Неизвестный узел: {type(node).__name__}")

    return _eval(tree)


# ─────────────────────────────────────────────
# Символьные вычисления через SymPy
# ─────────────────────────────────────────────
SYMPY_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


def _preprocess_sympy(expr_str: str) -> str:
    """Заменяет ^ на ** для sympy, убирает русские символы."""
    expr_str = expr_str.replace("^", "**")
    expr_str = expr_str.replace("√", "sqrt")
    expr_str = expr_str.replace("×", "*")
    expr_str = expr_str.replace("÷", "/")
    expr_str = expr_str.replace("−", "-")
    return expr_str


def symbolic_simplify(expr_str: str) -> str:
    """Упрощает выражение: (x+1)^2 → x^2 + 2x + 1."""
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        result = sp.simplify(expr)
        return str(result)
    except Exception as e:
        return f"Ошибка: {e}"


def symbolic_expand(expr_str: str) -> str:
    """Раскрывает скобки."""
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        return str(sp.expand(expr))
    except Exception as e:
        return f"Ошибка: {e}"


def symbolic_factor(expr_str: str) -> str:
    """Раскладывает на множители."""
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        return str(sp.factor(expr))
    except Exception as e:
        return f"Ошибка: {e}"


def symbolic_solve(equation_str: str, var: str = "x") -> str:
    """
    Решает уравнение. Формат: 'x^2 - 4 = 0' или '2x + 3 = 7'.
    Возвращает корни.
    """
    try:
        if "=" in equation_str:
            left, right = equation_str.split("=", 1)
            eq = sp.Eq(parse_expr(_preprocess_sympy(left), transformations=SYMPY_TRANSFORMS),
                       parse_expr(_preprocess_sympy(right), transformations=SYMPY_TRANSFORMS))
        else:
            eq = parse_expr(_preprocess_sympy(equation_str), transformations=SYMPY_TRANSFORMS)

        x = sp.Symbol(var)
        solutions = sp.solve(eq, x)
        if not solutions:
            return "Решений нет"
        return f"{var} = " + ", ".join(str(s) for s in solutions)
    except Exception as e:
        return f"Ошибка: {e}"


def symbolic_derivative(expr_str: str, var: str = "x") -> str:
    """Производная."""
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        x = sp.Symbol(var)
        return str(sp.diff(expr, x))
    except Exception as e:
        return f"Ошибка: {e}"


def symbolic_integral(expr_str: str, var: str = "x") -> str:
    """Неопределённый интеграл."""
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        x = sp.Symbol(var)
        return str(sp.integrate(expr, x)) + " + C"
    except Exception as e:
        return f"Ошибка: {e}"


def symbolic_limit(expr_str: str, var: str = "x", point: str = "0") -> str:
    """Предел функции в точке."""
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        x = sp.Symbol(var)
        pt = sp.sympify(point)
        return str(sp.limit(expr, x, pt))
    except Exception as e:
        return f"Ошибка: {e}"


def symbolic_evaluate(expr_str: str, var: str = "x", value: float = 0) -> str:
    """Подставляет значение переменной и вычисляет."""
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        x = sp.Symbol(var)
        result = expr.subs(x, value)
        return str(sp.N(result))
    except Exception as e:
        return f"Ошибка: {e}"


# ─────────────────────────────────────────────
# Системы счисления
# ─────────────────────────────────────────────
def to_base(n: int, base: int) -> str:
    """Переводит число в заданную систему счисления."""
    if base == 10:
        return str(n)
    if n == 0:
        return "0"
    negative = n < 0
    n = abs(n)
    digits = "0123456789ABCDEF"
    result = ""
    while n > 0:
        result = digits[n % base] + result
        n //= base
    return ("-" if negative else "") + result


def convert_bases(number_str: str, from_base: int) -> dict:
    """Переводит число из одной системы во все основные."""
    try:
        n = int(number_str.strip(), from_base)
        return {
            "dec": str(n),
            "bin": bin(n)[2:],
            "oct": oct(n)[2:],
            "hex": hex(n)[2:].upper(),
        }
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# Графики
# ─────────────────────────────────────────────
def get_plot_data(expr_str: str, var: str = "x",
                  x_min: float = -10, x_max: float = 10,
                  points: int = 500) -> dict:
    """
    Возвращает данные для построения графика: [{'x': ..., 'y': ...}, ...].
    Не рисует сам - только данные.
    """
    try:
        expr = parse_expr(_preprocess_sympy(expr_str), transformations=SYMPY_TRANSFORMS)
        x = sp.Symbol(var)
        f = sp.lambdify(x, expr, modules=["math"])

        xs = []
        ys = []
        step = (x_max - x_min) / points
        for i in range(points + 1):
            xv = x_min + i * step
            try:
                yv = f(xv)
                if isinstance(yv, complex):
                    continue
                if math.isnan(yv) or math.isinf(yv):
                    continue
                # Ограничиваем огромные значения
                if abs(yv) > 1e6:
                    continue
                xs.append(xv)
                ys.append(yv)
            except Exception:
                continue

        return {"x": xs, "y": ys, "error": None}
    except Exception as e:
        return {"x": [], "y": [], "error": str(e)}

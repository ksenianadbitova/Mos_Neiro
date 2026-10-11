"""Физика: формулы, решения и обсуждение."""
import re
from logic.web_search import search_wikipedia, explain_topic


FORMULAS = {
    "скорость": ("v = S / t", "v — скорость, S — путь, t — время"),
    "путь": ("S = v · t", "S — путь, v — скорость, t — время"),
    "ускорение": ("a = (v − v₀) / t", "a — ускорение"),
    "сила": ("F = m · a", "F — сила (Н), m — масса (кг), a — ускорение (м/с²)"),
    "вес": ("P = m · g", "P — вес (Н), g ≈ 9.8 м/с²"),
    "работа": ("A = F · S", "A — работа (Дж)"),
    "мощность": ("N = A / t", "N — мощность (Вт)"),
    "давление": ("p = F / S", "p — давление (Па)"),
    "плотность": ("ρ = m / V", "ρ — плотность (кг/м³)"),
    "закон ома": ("I = U / R", "I — ток (А), U — напряжение (В), R — сопротивление (Ом)"),
    "энергия кинетическая": ("Eₖ = m·v² / 2", "Eₖ — кинетическая энергия (Дж)"),
    "энергия потенциальная": ("Eₚ = m·g·h", "Eₚ — потенциальная энергия (Дж)"),
    "импульс": ("p = m · v", "p — импульс (кг·м/с)"),
}


def list_formulas() -> str:
    lines = ["📚 База формул:"]
    for key, (formula, desc) in sorted(FORMULAS.items()):
        lines.append(f"\n• {key.capitalize()}: {formula}\n   {desc}")
    return "\n".join(lines)


def find_formula(query: str) -> str:
    q = query.lower().strip()
    for key, (formula, desc) in FORMULAS.items():
        if key in q:
            return (f"📐 Формула для «{key}»:\n\n   {formula}\n\n"
                    f"💡 {desc}\n\n🔍 Спроси: «объясни {key}»")
    return explain_topic(f"формула {query} физика")


def solve_step_by_step(problem: str) -> str:
    text = problem.strip()
    if not text:
        return "🤔 Введи задачу."

    lines = [f"📝 Задача: {text}\n", "🔍 Разбор по шагам:\n"]
    numbers = re.findall(r"[-+]?\d+(?:[.,]\d+)?", text)
    if numbers:
        nums = [float(n.replace(",", ".")) for n in numbers]
        lines.append(f"Шаг 1. Данные: {nums}")
    else:
        lines.append("Шаг 1. Числовых данных нет — задача качественная.")

    subject = ""
    for key in FORMULAS:
        if key in text.lower():
            subject = key
            formula, desc = FORMULAS[key]
            lines.append(f"Шаг 2. Формула: {formula}")
            lines.append(f"       ({desc})")
            break

    if not subject:
        wiki = search_wikipedia(f"физика {text[:60]}")
        if wiki["found"]:
            lines.append(f"Шаг 2. Статья: {wiki['title']}")
            lines.append(f"       {wiki['summary'][:400]}")
            lines.append(f"\n🔗 {wiki['url']}")
        else:
            lines.append("Шаг 2. Формула не определена. Уточни задачу.")

    lines.append("\nШаг 3. Подставь значения и вычисли.")
    lines.append("Шаг 4. Проверь единицы СИ.")
    return "\n".join(lines)


def discuss(solution: str, question: str) -> str:
    return explain_topic(question)

"""
Конвертация единиц измерения через pint.
"""
try:
    import pint
    ureg = pint.UnitRegistry()
    PINT_OK = True
except ImportError:
    ureg = None
    PINT_OK = False


CATEGORIES = {
    "📏 Длина": ["m", "cm", "mm", "km", "inch", "foot", "yard", "mile", "nautical_mile"],
    "⚖️ Масса": ["kg", "g", "mg", "ton", "pound", "ounce"],
    "⏱ Время": ["second", "minute", "hour", "day", "week", "year"],
    "🌡 Температура": ["degC", "degF", "kelvin"],
    "📐 Площадь": ["m**2", "cm**2", "km**2", "hectare", "acre", "foot**2"],
    "🧊 Объём": ["m**3", "liter", "ml", "cm**3", "gallon", "pint"],
    "🚀 Скорость": ["m/s", "km/h", "mile/hour", "knot"],
    "⚡ Энергия": ["joule", "calorie", "kilocalorie", "kWh", "electron_volt"],
    "🔌 Мощность": ["watt", "kilowatt", "horsepower"],
    "🌐 Давление": ["pascal", "bar", "atm", "mmHg", "psi"],
    "📊 Частота": ["hertz", "kilohertz", "megahertz", "gigahertz"],
    "🔊 Угол": ["degree", "radian", "gradian"],
}


def convert(value: float, from_unit: str, to_unit: str) -> dict:
    if not PINT_OK:
        return {"error": "pint не установлен. Установи: python -m pip install pint"}
    try:
        quantity = value * ureg(from_unit)
        converted = quantity.to(to_unit)
        return {
            "result": converted.magnitude,
            "unit": str(converted.units),
            "formatted": f"{converted.magnitude:.6g} {converted.units}",
            "error": None,
        }
    except Exception as e:
        return {"error": str(e)}


def get_categories() -> dict:
    """Возвращает категории единиц."""
    return CATEGORIES


def list_categories() -> dict:
    """Алиас для get_categories (обратная совместимость)."""
    return CATEGORIES


def is_available() -> bool:
    return PINT_OK

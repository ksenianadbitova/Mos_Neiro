"""
Универсальный поиск и перевод без API-ключей.
- ddgs — веб-поиск
- Wikipedia API — термины
- MyMemory + Google — перевод
"""
import re
import time
import requests
from bs4 import BeautifulSoup
import wikipediaapi
from urllib.parse import quote, urlparse, parse_qs

try:
    from ddgs import DDGS
    DDGS_OK = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDGS_OK = True
    except ImportError:
        DDGS_OK = False


WIKI_RU = wikipediaapi.Wikipedia(
    user_agent="Umnik/1.0 (educational)",
    language="ru",
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}


_TRANSLATE_CACHE = {}


def _clean(t):
    return re.sub(r"\s+", " ", t or "").strip()


# ───────────────────────────────────────────────
# ПЕРЕВОД
# ───────────────────────────────────────────────

TRANSLATE_MARKERS = [
    "переведи", "перевод", "перевести", "как переводится",
    "translate", "что значит по-английски",
    "как будет по-английски", "как будет по-русски",
    "как по-английски", "как по-русски",
]


def is_translate_request(query: str) -> bool:
    q = query.lower()
    return any(m in q for m in TRANSLATE_MARKERS)


def _extract_for_translate(query: str) -> str:
    t = query
    markers = [
        "переведи на английский", "переведи на русский",
        "как будет по-английски", "как будет по-русски",
        "как по-английски", "как по-русски",
        "что значит по-английски",
        "перевод слова", "перевести",
        "переведи", "перевод", "translate",
        "как переводится",
    ]
    for m in markers:
        t = re.sub(re.escape(m), "", t, flags=re.IGNORECASE)
    return t.strip(" :.,!?\"'«»")


def _translate_mymemory(text: str, target: str) -> str:
    try:
        source = "ru" if re.search(r"[а-яА-ЯёЁ]", text) else "en"
        if source == target:
            target = "en" if target == "ru" else "ru"

        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": f"{source}|{target}"},
            headers=HEADERS, timeout=10,
        )
        if r.status_code != 200:
            return ""
        data = r.json()
        translated = (data.get("responseData", {})
                          .get("translatedText", "") or "").strip()
        if translated and translated.lower() != text.lower():
            return translated
        return ""
    except Exception:
        return ""


def _translate_google(text: str, target: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        for attempt in range(2):
            try:
                tr = GoogleTranslator(source="auto", target=target)
                result = tr.translate(text)
                if result:
                    return result
            except Exception as e:
                if "too many" in str(e).lower() or "429" in str(e):
                    time.sleep(2)
                    continue
                return ""
    except ImportError:
        pass
    return ""


def translate_text(text: str, target: str = None) -> str:
    """Перевод: сначала офлайн (Argos), потом онлайн (MyMemory, Google)."""
    if not text or not text.strip():
        return ""
    text = text.strip()

    if target is None:
        target = "en" if re.search(r"[а-яА-ЯёЁ]", text) else "ru"

    key = (text.lower(), target)
    if key in _TRANSLATE_CACHE:
        return _TRANSLATE_CACHE[key]

    # 1. Офлайн-перевод через Argos Translate
    offline = _translate_argos(text, target)
    if offline:
        _TRANSLATE_CACHE[key] = offline
        return offline

    # 2. Онлайн через MyMemory
    result = _translate_mymemory(text, target)
    if result:
        _TRANSLATE_CACHE[key] = result
        return result

    # 3. Онлайн через Google
    result = _translate_google(text, target)
    if result:
        _TRANSLATE_CACHE[key] = result
        return result

    return "Не удалось перевести. Попробуй снова."


def _translate_argos(text: str, target: str) -> str:
    """Офлайн-перевод через Argos Translate. Если пакетов нет — вернёт ''."""
    try:
        import argostranslate.translate as tr
    except ImportError:
        return ""

    source = "ru" if re.search(r"[а-яА-ЯёЁ]", text) else "en"
    if source == target:
        target = "en" if target == "ru" else "ru"

    try:
        result = tr.translate(text, source, target)
        if result and result.strip() and result.strip().lower() != text.lower():
            return result.strip()
    except Exception:
        pass
    return ""


def _translate_mymemory(text: str, target: str) -> str:
    """MyMemory — публичный API, работает онлайн."""
    try:
        source = "ru" if re.search(r"[а-яА-ЯёЁ]", text) else "en"
        if source == target:
            target = "en" if target == "ru" else "ru"

        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": f"{source}|{target}"},
            headers=HEADERS, timeout=10,
        )
        if r.status_code != 200:
            return ""
        data = r.json()
        translated = (data.get("responseData", {})
                          .get("translatedText", "") or "").strip()
        if translated and translated.lower() != text.lower():
            return translated
        return ""
    except Exception:
        return ""


def _translate_google(text: str, target: str) -> str:
    """Google через deep-translator (может упасть при лимите)."""
    try:
        from deep_translator import GoogleTranslator
        for attempt in range(2):
            try:
                tr = GoogleTranslator(source="auto", target=target)
                result = tr.translate(text)
                if result:
                    return result
            except Exception as e:
                if "too many" in str(e).lower() or "429" in str(e):
                    time.sleep(2)
                    continue
                return ""
    except ImportError:
        pass
    return ""


def _ddgs_search(query: str, max_results: int = 10) -> list:
    if not DDGS_OK:
        return []
    try:
        with DDGS() as ddgs:
            try:
                results = list(ddgs.text(query, region="ru-ru",
                                          safesearch="moderate",
                                          max_results=max_results))
            except Exception:
                results = list(ddgs.text(query, max_results=max_results))
        out = []
        for r in results:
            url = r.get("href", "")
            if not url.startswith("http"):
                continue
            out.append({
                "title": _clean(r.get("title", ""))[:200],
                "url": url,
                "snippet": _clean(r.get("body", ""))[:300],
                "source": "Интернет",
            })
        return out
    except Exception:
        return []


def _fallback_search(query: str, max_results: int = 10) -> list:
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS, timeout=12,
        )
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for res in soup.select(".result")[:max_results]:
            a = res.select_one(".result__a")
            sn = res.select_one(".result__snippet")
            if not a:
                continue
            href = a.get("href", "")
            if href.startswith("//duckduckgo.com/l/"):
                qs = parse_qs(urlparse("https:" + href).query)
                href = qs.get("uddg", [href])[0]
            if not href.startswith("http"):
                continue
            results.append({
                "title": _clean(a.get_text())[:200],
                "url": href,
                "snippet": _clean(sn.get_text())[:300] if sn else "",
                "source": "Интернет",
            })
        return results
    except Exception:
        return []


def _wiki_results(query: str, max_results: int = 5) -> list:
    results = []
    try:
        page = WIKI_RU.page(query)
        if page.exists():
            results.append({
                "title": page.title,
                "url": page.fullurl,
                "snippet": _clean(page.summary)[:250],
                "source": "Википедия",
            })
    except Exception:
        pass

    try:
        titles = WIKI_RU.search(query, results=max_results + 3)
    except Exception:
        titles = []

    existing = {r["url"] for r in results}
    for t in titles:
        if len(results) >= max_results:
            break
        try:
            p = WIKI_RU.page(t)
            if p.exists() and p.fullurl not in existing:
                results.append({
                    "title": p.title,
                    "url": p.fullurl,
                    "snippet": _clean(p.summary)[:250],
                    "source": "Википедия",
                })
                existing.add(p.fullurl)
        except Exception:
            continue
    return results


def search_web(query: str, max_results: int = 12) -> list:
    if not query or not query.strip():
        return []
    query = query.strip()
    combined = []
    seen = set()

    def _add(items):
        for it in items:
            url = it.get("url", "")
            if not url or url in seen:
                continue
            seen.add(url)
            combined.append(it)

    _add(_wiki_results(query, max_results=5))
    if len(combined) < max_results:
        _add(_ddgs_search(query, max_results=max_results))
    if len(combined) < max_results:
        _add(_fallback_search(query, max_results=max_results))

    if not combined:
        return [{
            "title": "Ничего не найдено",
            "url": "",
            "snippet": "Попробуй другой запрос.",
            "source": "",
        }]
    return combined[:max_results]


def search_wikipedia(query, lang="ru", sentences=5):
    try:
        page = WIKI_RU.page(query)
    except Exception:
        page = None
    if page is None or not page.exists():
        try:
            lst = WIKI_RU.search(query, results=5)
        except Exception:
            lst = []
        if not lst:
            return {"found": False, "title": "", "url": "", "summary": "", "suggestions": []}
        page = WIKI_RU.page(lst[0])

    summary = page.summary or ""
    parts = summary.split(". ")
    short = ". ".join(parts[:sentences])
    if short and not short.endswith("."):
        short += "."
    try:
        sug = WIKI_RU.search(query, results=5)
    except Exception:
        sug = []
    return {
        "found": True, "title": page.title, "url": page.fullurl,
        "summary": short, "suggestions": sug,
    }


def explain_topic(topic: str) -> str:
    if not topic or not topic.strip():
        return "🤔 Пустой запрос."

    if is_translate_request(topic):
        word = _extract_for_translate(topic)
        if not word:
            return ("🌐 Напиши, что перевести. Например:\n"
                    "• «переведи hello»\n"
                    "• «как по-английски спасибо»")
        translated = translate_text(word)
        if translated and not translated.startswith(("Не удалось", "Ошибка")):
            if re.search(r"[а-яА-ЯёЁ]", word):
                direction = "🇷🇺 → 🇬🇧"
            else:
                direction = "🇬🇧 → 🇷🇺"
            return f"🌐 Перевод:\n\n{direction}  «{word}» → «{translated}»"
        return f"😕 {translated}"

    res = search_wikipedia(topic)
    if res["found"]:
        text = f"📖 {res['title']}\n\n{res['summary']}\n\n🔗 {res['url']}"
        if res["suggestions"]:
            text += "\n\n💡 Похожие темы: " + ", ".join(res["suggestions"][:5])
        return text

    web = search_web(topic, max_results=5)
    if web and web[0].get("url"):
        lines = [f"🌐 Нашёл в интернете по запросу «{topic}»:\n"]
        for it in web[:5]:
            lines.append(f"\n• {it['title']}\n  {it['url']}")
            if it.get("snippet"):
                lines.append(f"  {it['snippet'][:200]}")
        return "\n".join(lines)

    return f"😕 Не нашёл информацию по теме «{topic}»."


def fetch_page_text(url, max_chars=3000):
    try:
        r = requests.get(url, timeout=15, headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:max_chars]
    except Exception as e:
        return f"❌ Ошибка загрузки: {e}"

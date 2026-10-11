"""Экспорт истории чата в JSON и Markdown."""
import json
from datetime import datetime
from pathlib import Path
from database import DB_PATH
import sqlite3


def export_session(session_id: int, format: str = "md", output_path: str = None) -> str:
    """
    Экспортирует сессию чата.
    format: 'md' или 'json'.
    output_path: если None — сохраняется в папку output/.
    """
    # Получаем сообщения
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title FROM chat_sessions WHERE id = ?", (session_id,))
    row = cur.fetchone()
    title = row[0] if row else "Чат"
    cur.execute(
        "SELECT role, content, timestamp FROM chat_messages "
        "WHERE session_id = ? ORDER BY id",
        (session_id,),
    )
    messages = cur.fetchall()
    conn.close()

    if not messages:
        return "❌ В сессии нет сообщений"

    # Определяем путь
    if output_path is None:
        out_dir = Path(__file__).parent.parent / "output"
        out_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:40]
        output_path = out_dir / f"chat_{safe_title}_{ts}.{format}"
    else:
        output_path = Path(output_path)

    # Формируем содержимое
    if format == "json":
        data = {
            "title": title,
            "exported_at": datetime.now().isoformat(),
            "messages": [
                {"role": r, "content": c, "timestamp": t}
                for r, c, t in messages
            ],
        }
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    else:  # md
        lines = [f"# {title}", "", f"*Экспортировано: {datetime.now():%d.%m.%Y %H:%M}*", ""]
        for role, content, ts in messages:
            icon = "👤" if role == "user" else "🤖"
            who = "**Вы**" if role == "user" else "**МосНейро**"
            lines.append(f"### {icon} {who}")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append(f"*{ts}*")
            lines.append("")
            lines.append("---")
            lines.append("")
        output_path.write_text("\n".join(lines), encoding="utf-8")

    return f"✅ Экспортировано в:\n{output_path}"

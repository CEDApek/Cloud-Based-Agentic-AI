import json
from pathlib import Path

"""
    1. ADD_TODO   : add a task
    2. LIST_TODOS : shows tasks (stored in todos.json)
"""

DATA_DIR = Path("data")
TODO_FILE = DATA_DIR / "todos.json"

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _load() -> list[dict]:
    _ensure_data_dir()
    if not TODO_FILE.exists():
        return []
    return json.loads(TODO_FILE.read_text(encoding="utf-8"))

def _save(items: list[dict]) -> None:
    TODO_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def add_todo(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "Refused: empty todo."
    items = _load()
    items.append({"text": text, "done": False})
    _save(items)
    return f"OK: added todo ({len(items)} total)."

def list_todos() -> str:
    items = _load()
    if not items:
        return "No todos yet."
    out = []
    for i, item in enumerate(items, start=1):
        mark = "x" if item.get("done") else " "
        out.append(f"{i}. [{mark}] {item.get('text','')}")
    return "\n".join(out)
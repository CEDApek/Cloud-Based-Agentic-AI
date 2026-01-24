from pathlib import Path

DATA_DIR = Path("data")
NOTES_FILE = DATA_DIR / "notes.txt"

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def write_note(text: str) -> str:
    """Append a note to data/notes.txt"""
    _ensure_data_dir()
    text = (text or "").strip()
    if not text:
        return "Refused: empty note."
    with NOTES_FILE.open("a", encoding="utf-8") as f:
        f.write(text + "\n")
    return f"OK: wrote note ({len(text)} chars)."

def read_notes(last_n: int = 10) -> str:
    """Read last N notes"""
    _ensure_data_dir()
    if not NOTES_FILE.exists():
        return "No notes yet."
    lines = NOTES_FILE.read_text(encoding="utf-8").splitlines()
    tail = lines[-last_n:] if last_n > 0 else lines
    if not tail:
        return "No notes yet."
    return "\n".join(f"- {line}" for line in tail)

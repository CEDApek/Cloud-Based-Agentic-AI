# Agent System

## 1). main.py `/src/main.py`

> act as an entry point (reads goal from command line and starts the agent)

```python
import sys
from src.agent import MiniAgent

def main():
    goal = " ".join(sys.argv[1:]).strip()
    if not goal:
        goal = "Save a note about what agentic AI is, then show notes."
    MiniAgent(goal).run()

if __name__ == "__main__":
    main()
```

* `sys` : access to command-line arguments
  
  * `MiniAgent` : class from the `/src/agent.py`

> ```python
> def main():
>     goal = " ".join(sys.argv[1:]).strip()
> ```
> 
> **Format :** `sys.argv` = `python3 -m src.main Save a note`
> 
> * `sys.argv[0]` = `src.main` is the script/module name
> 
> * `sys.argv[1:]` = everything starting from `sys.argv[1]`++ ("Save a note")
> 
> * `-m` : Python sets it up so the `__main__` block runs

* the if-else sets a default goal if we run it with no goal

``MiniAgent(goal).run()`` :

* creates an agent instance, then starts the agent loop

<br>

## 2). agent.py `/src/agent.py`

> contains the agent loop (decide $\rightarrow$ act $\rightarrow$ observe $\rightarrow$ repeat)

```python
from dataclasses import dataclass
from typing import Literal, Optional
from src.tools.notes import write_note, read_notes
```

* `dataclass` : lets us define simple "data containers" without boilerplate

* `Literal` : restricts values to specific strings (limit the options)

* `Optional[str]` : either `str` or `None`

* `write_note`, `read_notes` : tool function from `/src/tools/notes`

```python
ActionKind = Literal["WRITE_NOTE", "READ_NOTES", "DONE"]
```

* Agent can only choose between three actions

```python
@dataclass
class Action:
    kind: ActionKind
    payload: Optional[str] = None
```

an `Action` consists of : `e.g.` : `Action("WRITE_NOTE", payload="hello")`

* `kind` : what kind of action (`ActionKind`)

* `payload` : data (text to write : `write_note`)

##### Agent Class : `MiniAgent`

> Consists of :
> 
> * the goal
> 
> * step counter
> 
> * decision logic
> 
> * the main agentic loop

**Constructor :**

```python
def __init__(self, goal: str):
    self.goal = goal.strip()
    self.step = 0
    self.max_steps = 6
```

* `goal` : the prompt we inject upon calling

* `step` : show many actions taken

* `max_steps` : prevents infinite loops (pre-defined)

**Complementary Function : `extract_note_text`**

```python
def extract_note_text(goal: str) -> str | None:
    g = goal.strip()
    lower = g.lower()
    for marker in ("note:", "list:", "text:"):
        index = lower.find(marker)
        if index != -1:
            content = g[index + len(marker):].strip()
            return content if content else None
    return None
```

* This function extract the actual payload rather than re-writing the whole prompt

###### **decide()**

> This is the planner : signal the `Action()`

```python
    def decide(self) -> Action:
        """
        Rule-based planner (free) that only writes notes if asked.

        Plan:
        - If user asked to save/write/remember/note:
            step 0 -> WRITE_NOTE
            step 1 -> (optional) READ_NOTES if asked
            step 2 -> DONE
        - If user only asked to show/list/read notes:
            step 0 -> READ_NOTES
            step 1 -> DONE
        - Otherwise:
            step 0 -> DONE
        """
        g = self.goal.lower()

        wants_read = any(k in g for k in ["show", "list", "read", "notes"])

        # Writing should require a *clear* write intent (not just the word "notes")
        wants_write = any(k in g for k in ["save", "write", "remember"]) or bool(
            re.search(r"\b(save|write)\s+a\s+note\b|\b(note:)\b", g)
        )

        # Case 1: User requested writing a note
        if wants_write:
            if self.step == 0:
                # For now, we store the whole goal as the note content.
                # Later we can parse only the part after "save a note:" etc.
                note_text = extract_note_text(self.goal) # returns either None or the payload part
                payload = note_text if note_text is not None else self.goal
                return Action("WRITE_NOTE", payload=payload)


            if self.step == 1 and wants_read:
                return Action("READ_NOTES")

            return Action("DONE")

        # Case 2: User did NOT request writing, but did request reading
        if wants_read:
            if self.step == 0:
                return Action("READ_NOTES")
            return Action("DONE")

        # Case 3: No write/read requested
        return Action("DONE")
```

* `g` : is the goal (in lower case)
1. Search the indicator to write a note (append), then continue search for other keyword
   
   * Called the complementary function to check for any key word specified for certain payload, if None just write the whole prompt

2. then we search for any word indicating "read" then signal `Read` action

3. Until no keywords match, finish (`"DONE"`)

###### **act()**

> The action called by `decide()`

```python
def act(self, action: Action) -> str:
    if action.kind == "WRITE_NOTE":
        return write_note(action.payload or "")
    if action.kind == "READ_NOTES":
        return read_notes(last_n=10)
    return "Finished."
```

If action is `WRITE_NOTE` :

* call function tool `write_note`

* returns the payload, if empty just write an empty string `""`

If actions is `READ_NOTES` :

* read last 10 notes

* return them as string

If action id `DONE` : return a simple message

###### **run()**

> the agent loop

```python
    def run(self) -> None:
        print(f"\n[GOAL] {self.goal}\n")
        while self.step < self.max_steps:
            action = self.decide()
            print(f"[STEP {self.step+1}] decide -> {action.kind}")
            result = self.act(action)
            print(f"[STEP {self.step+1}] observe -> {result}\n")

            self.step += 1
            if action.kind == "DONE":
                break
```

1. Prints the goal first

2. Loop until it hits the maximum steps (can exit early)
   
   1. define the `action` by calling `decide()` (planner), then print the decision
   
   2. execute `act()` based on the `action` and print result
   
   3. Increment steps If done, exit early

<br>

## 3). notes.py `src/tools/notes.py`

> a tool module
> 
> * how agent "touches the actual world"

```python
from pathlib import Path

DATA_DIR = Path("data")
NOTES_FILE = DATA_DIR / "notes.txt"

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
```

* `Path` : to handle file paths than raw strings

* directory to save notes to `data/` folder

* file path is `data/notes.txt`
  
  * will create `data/` if it doesn't exist

**Writing notes**

```python
def write_note(text: str) -> str:
    """Append a note to data/notes.txt"""
    _ensure_data_dir()
    text = (text or "").strip()
    if not text:
        return "Refused: empty note."
    with NOTES_FILE.open("a", encoding="utf-8") as f:
        f.write(text + "\n")
    return f"OK: wrote note ({len(text)} chars)."
```

1. Make sure folder exist

2. Clean the input text

3. Open file in append mode (no re-write)

4. Return a status message for any notes written

**Reading notes**

```python
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
```

1. Read last N lines

2. Then turns the last lines into a bullet list string

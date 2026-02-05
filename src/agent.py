from dataclasses import dataclass
from typing import Literal, Optional
import re

from src.tools.notes import write_note, read_notes

ActionKind = Literal["WRITE_NOTE", "READ_NOTES", "DONE"]

def extract_note_text(goal: str) -> str | None:
    """
    Extract note content from a goal string.
    Examples:
      "save a note: hello" -> "hello"
      "write a note: buy milk, then show notes" -> "buy milk"
    Returns None if no explicit "note:" marker is found.
    """
    g = goal.strip()
    lower = g.lower()
    marker = "note:"
    idx = lower.find(marker)
    if idx == -1:
        return None
    content = g[idx + len(marker):].strip()
    return content if content else None


@dataclass
class Action:
    kind: ActionKind
    payload: Optional[str] = None

class MiniAgent:
    """
    Agentic AI (minimal form):
        - has a goal
        - chooses next action
        - uses tools
        - observes results
        - repeats
    """

    """ for each prompt, they hold the goal, steps, and max steps taken """
    def __init__(self, goal: str):
        self.goal = goal.strip()
        self.step = 0
        self.max_steps = 6

    """ Agentic Planner """
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
                note_text = extract_note_text(self.goal)
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



    def act(self, action: Action) -> str:
        if action.kind == "WRITE_NOTE":
            return write_note(action.payload or "")
        if action.kind == "READ_NOTES":
            return read_notes(last_n=10)
        return "Finished."

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

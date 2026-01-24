from dataclasses import dataclass
from typing import Literal, Optional

from src.tools.notes import write_note, read_notes

ActionKind = Literal["WRITE_NOTE", "READ_NOTES", "DONE"]

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

    """ This is the planner """
    def decide(self) -> Action:
        """
        For now: rule-based 'planner' (free).
        Later: replace with a real LLM planner.
        """
        g = self.goal.lower()

        if self.step == 0:
            # Always record the goal first (state change).
            return Action("WRITE_NOTE", payload=f"Goal: {self.goal}")
        # below we check for certain keyowrd indicating "reading"
        if any(k in g for k in ["show", "list", "read", "notes", "check", "prove"]):
            return Action("READ_NOTES")

        # Default finish.
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

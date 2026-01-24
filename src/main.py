import sys
from src.agent import MiniAgent

def main():
    goal = " ".join(sys.argv[1:]).strip()
    if not goal:
        goal = "Save a note about what agentic AI is, then show notes."
    MiniAgent(goal).run()

if __name__ == "__main__":
    main()

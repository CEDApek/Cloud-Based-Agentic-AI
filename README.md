# Cloud-Based-Agentic-AI

Mini Project aiming for basic concept and understanding of AI and cloud technology in order to understand the security.

Goal :

- Build minimal agent loop
- Provide tools
- Study the boundaries
- Later: deploy to cloud safely (For Upcoming Project)



## What this project demonstrates (plain-language)

This repository is a **minimal agentic AI loop**. An “agent” is software that:

1. **Receives a goal** (the user’s request),

2. **Plans the next step** (decides an action),

3. **Uses a tool** (reading or writing notes, add to-do list),

4. **Observes the result**, and

5. **Repeats** until it is done.

In this project, the “planner” is intentionally simple (rule-based).

## How to run it (local)

```bash
python -m src.main "Write a note about agentic AI, then show notes"
```

If you don’t pass a goal, it uses a default goal that writes a note and then reads the notes. (default escape route)

## How the agent works (step-by-step)
(To be Completed, later on, I'm focussing on Bigger Project)

**LLM API (if/when you add a real model):**

Use an **OpenAI-compatible API** so you can swap between providers or local models (e.g., OpenAI, Azure OpenAI, or local LLM servers that implement the same API).

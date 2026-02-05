# Cloud-Based-Agentic-AI

Mini Project aiming for basic concept and understanding of AI and cloud technology in order to understand the security.

Goal :

- Build minimal agent loop
- Provide tools
- Study the boundaries
- Later: deploy to cloud safely



## What this project demonstrates (plain-language)

This repository is a **minimal agentic AI loop**. An “agent” is software that:

1. **Receives a goal** (the user’s request),

2. **Plans the next step** (decides an action),

3. **Uses a tool** (like reading or writing notes),

4. **Observes the result**, and

5. **Repeats** until it is done.

In this project, the “planner” is intentionally simple (rule-based). In real systems, you can replace the planner with an LLM (Large Language Model) that decides the next action. This makes the code easier to understand before adding complex AI.

## How to run it (local)

```bash
python -m src.main "Write a note about agentic AI, then show notes"
```

If you don’t pass a goal, it uses a default goal that writes a note and then reads the notes.

## How the agent works (step-by-step)

1. **Goal is set** in `MiniAgent.__init__`.

2. **Planner decides** the next action in `MiniAgent.decide`:
-     First step always writes the goal into notes.
  
  - If the goal mentions “show/list/read/notes,” it reads notes.
  
  - Otherwise it finishes.
3. **Tool is executed** by `MiniAgent.act` using `write_note` or `read_notes`.

4. **Loop continues** in `MiniAgent.run` until DONE or max steps are reached.

## File-by-file explanation

- `src/main.py`

Entry point. Reads the goal from CLI arguments and runs the agent.

- `src/agent.py`

Defines the agent loop, the action types, the planner (`decide`), and the action executor (`act`).

- `src/tools/notes.py`

A simple tool that reads/writes notes to `data/notes.txt`.

- `src/__init__.py`, `src/tools/__init__.py`

Package markers so Python can import the modules.

## Which cloud tech to use (free & open-source)

If you want cloud-like storage without paying for AWS, use an **S3-compatible open-source object store**:

**Recommended: MinIO (open-source S3-compatible storage)**

- It is free, self-hostable, and widely used.

- It exposes the **S3 API**, so your code can talk to it the same way it would talk to AWS S3.

- You can run MinIO locally, on a VM, or in a small Kubernetes cluster.

Other open-source S3-compatible options include **Ceph RGW** or **LocalStack** (for local emulation), but MinIO is the simplest.

## Which API to select

**Storage API:**

Use the **S3 API** (because MinIO and other tools support it). This keeps your code portable—later you can switch to AWS S3 with minimal changes.

**LLM API (if/when you add a real model):**

Use an **OpenAI-compatible API** so you can swap between providers or local models (e.g., OpenAI, Azure OpenAI, or local LLM servers that implement the same API).

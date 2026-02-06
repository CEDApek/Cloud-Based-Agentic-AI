from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agent import MiniAgent

app = FastAPI(title="Agent Lab API", version="0.1")

# Client Request Structure
class RunRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=500)

# Server Response Structure
class RunResponse(BaseModel):
    goal: str
    steps: list[dict]
    final: str | None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run", response_model=RunResponse)
def run_agent(req: RunRequest): # req is a local variable
    agent = MiniAgent(req.goal)
    return agent.run_collect()
""" 
    1. From request : {"goal": "Save a note"}
    2. Becomes req.goal == "Save a note"
    3. Then agent = MiniAgent(req.goal)
"""
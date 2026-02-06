from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agent import MiniAgent

app = FastAPI(title="Agent Lab API", version="0.1")

class RunRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=500)

class RunResponse(BaseModel):
    goal: str
    steps: list[dict]
    final: str | None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run", response_model=RunResponse)
def run_agent(req: RunRequest):
    agent = MiniAgent(req.goal)
    return agent.run_collect()
# API Related System

## 1). agent.py function (`src/agent.py`)

```python
def run_collect(self) -> dict:
    """
    Run the agent and collect results in a JSON-friendly format.
    (Perfect for API responses.)
    """
    steps_out = []
    final = None

    while self.step < self.max_steps:
        action = self.decide()
        result = self.act(action)

        steps_out.append({
            "step": self.step + 1,
            "action": action.kind,
            "result": result,
        })

        self.step += 1
        final = result

        if action.kind == "DONE":
            break

    return {
        "goal": self.goal,
        "steps": steps_out,
        "final": final,
    }
```

* Still serves the same purpose as `run()` function but with JSON format

> Because APIs return data (in JSON format), printing to terminal isn't useful for a web client

<br>

## 2). API server file (`src/api.py`)

> ##### FastAPI basic usage :
> 
> * ```python
>   from fastapi import FastAPI
>   ```
> 
> * ```python
>   app = FastAPI()
>   ```
>   
>   * This to create a new app
> 
> * ```python
>   @app.get("/")
>   def root():
>       return {"Hello": ""World}
>   ```
>   
>   * When we visit `/` the `root()` function will be declared (with `GET` method)
> 
> **Routes** are created for different interactions
> 
> **Calling via `uvicorn` :**
> 
> ```bash
> uvicorn <file_name>:<app_name> --reload
> ```
> 
> * `--reload` : automatically reload file (for any code changes)

```python
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

@app.get("/status")
def health():
    return {"status": "ok"}

@app.post("/run", response_model=RunResponse)
def run_agent(req: RunRequest):
    agent = MiniAgent(req.goal)
    return agent.run_collect()
```

* we use the `FastAPI` framework (similar to Flask, but modern), used for :
  
  * Creating an API app
  
  * Define API routes (`/health`, `/run`)

* our API app name is "Agent Lab API"
  
  * later on we can load it via `uvicorn src.api:app --reload`

* `RunRequest()` : defines the shape of incoming JSON for `/run` (rejects bad request automatically)
  
  * ```json
    {
      "goal": "Save a note, then show notes"
    }
    ```

* `RunResponse` : shape of the response returned by `/run`
  
  * `goal: str` : Echoes the original goal
  
  * `steps: list[dict]` : list of steps taken by the agent
  
  * `final: str | None` : it is a string or None

* we defined a GET endpoint at `/health` to check "is the server alive"

* and another POST endpoint at `/run`, where responses must match `RunResponse`
  
  * `run_agent()` : sees the type `RunRequest`
  
  * Then reads the request body JSON, validates, convert to Python object
  
  * `e.g.` : 
    
    1. ```json
       {"goal": "Save a note"}
       ```
    
    2. Becomes :
       
       ```python
       req.goal == "Save a note"
       ```
    
    3. Then :
       
       ```python
       agent = MiniAgent(req.goal)
       ```

##### Flow :

1. Client sends :
   
   ```http
   POST /run
   Content-Type: application/json
   
   {
     "goal": "Save a note, then show notes"
   }
   ```

2. `FastAPI`
   
    then :
   
   * Parses JSON
   
   * Validates against `RunRequest`
   
   * calls `run_agent()`

3. Server then creates `MiniAgent` and runs `agent.run_collect()`

4. `FastAPI` then :
   
   * validates output against `RunResponse`
   
   * also converts to JSON
   
   * Sends response back to client

# Docker

> Right now, project runs because the OS has :
> 
> * Python version
> 
> * pip packages (`fastapi`, `uvicorn`)
> 
> * environment

Moving to another machine (or cloud VM), often breaks because :

* different Python version

* missing packages

* etc.

**What Docker does** $\rightarrow$ to package app into a container image

> **Image** = snapshot of Linux base + Python + dependencies + code
> 
> **Container** = running instance of the image

1. Build image once

2. Run it anywhere Docker exist

> ##### Matches Cloud because..
> 
> Cloud deployments are "Run this container somewhere"
> 
> * Docker is the universal format for deploying apps

<br>

#### How it Works

* **Dockerfile** : recipe for 
  
  * start from a base image
  
  * copy of the code
  
  * install dependencies
  
  * define command to run (pre defined bash command)

* **Ports** : Docker runs in its own "mini network"
  
  * must publish the port : inside container 8000, on your host machine: 8000 (`-p 8000:8000`)

* **Volumes** : to specify folder for data persistence (persistence across restarting docker) :
  
  * since app writes `data/notes.txt`, `data/todos.json` : `-v $(pwd)/data:/app/data`

****

## Project Related Docker Setup

> `requirements.txt` : already been set up earlier

1. Create `Dockerfile`
   
   ```bash
   nano Dockerfile
   ```

2. Add these lines :
   
   ```dockerfile
   # base system with PYthon installed
   FROM python:3.11-slim
   
   # Create working directory inside container ($ cd /app)
   WORKDIR /app
   
   # Copy dependency list first (copy file into container)
   COPY requirements.txt .
   
   # Install python dependencies
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy code to container
   COPY src ./src
   
   # Create data folder inside container (in case you don't mount a volume)
   RUN mkdir -p /app/data
   
   # Expose the API port (declares app uses port 8000)
   EXPOSE 8000
   
   # Start the FastAPI server (default command with the uvicorn)
   CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Build image**
   
   ```bash
   docker build -t agent-lab:0.1 .
   ```
   
   * `-t agent-lab:0.1` : names the image (+ version tag)
   
   Check image :
   
   ```bash
   docker images
   ```

4. Run the container
   
   **Quick run (no persistent data) :**
   
   ```bash
   docker run --rm -p 8000:8000 agent-lab:0.1
   ```
   
   **With data persistence :**
   
   ```bash
   docker run --rm \
     -p 8000:8000 \
     -v "$(pwd)/data:/app/data" \
     agent-lab:0.1
   ```

5. Test with :
   
   ```bash
   curl -s http://127.0.0.1:8000/status
   ```
   
   ```bash
   curl -s -X POST "http://127.0.0.1:8000/run" \
     -H "Content-Type: application/json" \
     -d '{"goal":"todo: docker works"}'
   ```

> **Open Docker Desktop :**
> 
> ```bash
> systemctl --user start docker-desktop
> ```
> 
> Stop :
> 
> ```bash
> systemctl --user stop docker-desktop
> ```

![](/home/ceda/Pictures/Screenshots/Screenshot_20260209_152053.png)

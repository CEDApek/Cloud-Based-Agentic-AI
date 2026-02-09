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
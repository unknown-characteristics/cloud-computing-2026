# Use official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure stdout/stderr are unbuffered
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y gcc libaio-dev libssl-dev make wget unzip && rm -rf /var/lib/apt/lists/*

COPY ./../web/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r ./requirements.txt && pip install watchdog

# Default command (change as needed)
CMD ["watchmedo", "auto-restart", "--directory=.", "--recursive", "--interval=1", "--pattern=*", "--debug-force-polling", "--", "python", "server.py"]

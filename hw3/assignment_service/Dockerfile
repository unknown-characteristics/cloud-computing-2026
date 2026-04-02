FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

RUN mv settings-env settings.env

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port $PORT"]

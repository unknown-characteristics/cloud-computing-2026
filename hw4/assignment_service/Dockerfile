FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# `ca-certificates` provides the full Mozilla CA bundle, which already contains
# every DigiCert root that Azure Database for MySQL Flexible Server uses
# (Global Root CA and Global Root G2). pymysql can use the bundle directly
# via DB_SSL_CA_PATH=/etc/ssl/certs/ca-certificates.crt — see core/database.py.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./main.py
COPY app ./app
RUN if [ -f settings-env ]; then mv settings-env settings.env; fi

EXPOSE 8000

# ${PORT:-8000} works on Cloud Run / App Engine ($PORT set), Azure App Service
# (defaults to 8000), and Azure Container Apps (sets PORT to targetPort).
CMD ["sh", "-c", "exec gunicorn -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120 main:app"]

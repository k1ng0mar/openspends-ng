FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

RUN apt-get update && apt-get install -y \
    default-jre-headless \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations on startup (safe to re-run — Alembic is idempotent)
RUN pip install --no-cache-dir alembic 2>/dev/null || true

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT

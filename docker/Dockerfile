# ----------------------- Base ─--------------------------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --------------------------- Dependencies ---------------------------------------------------
FROM base AS dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# -------------------------------- Production ----------------------------------------------------------
FROM base AS production

COPY --from=dependencies /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=dependencies /usr/local/bin /usr/local/bin

COPY . .

RUN mkdir -p logs uploads

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2"]
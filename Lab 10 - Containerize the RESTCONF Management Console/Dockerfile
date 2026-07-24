# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt "gunicorn>=23,<24"

COPY app.py config.py database.py restconf.py ./
COPY templates ./templates
COPY static ./static

RUN mkdir -p /app/instance && chown -R app:app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/routers', timeout=3)" || exit 1

CMD ["gunicorn", "--bind=127.0.0.1:8000", "--workers=1", "--threads=4", "--timeout=30", "--access-logfile=-", "--error-logfile=-", "app:app"]

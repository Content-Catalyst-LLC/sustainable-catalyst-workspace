# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY app ./app
EXPOSE 8089
CMD ["sh", "-c", "python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8089 --proxy-headers --forwarded-allow-ips='*'"]

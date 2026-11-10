# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY service.py ./
RUN useradd --system --uid 10001 scinterchange
USER 10001:10001
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8093"]

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY service.py ./
RUN useradd --system --uid 10001 scinterchange
USER 10001:10001
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8093"]

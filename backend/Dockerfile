FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8089
# Schema creation is an explicit maintenance action (python -m app.init_db),
# never an application startup side effect. Production runs with
# SC_WORKSPACE_AUTO_CREATE_SCHEMA=false.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8089", "--proxy-headers", "--forwarded-allow-ips=*"]

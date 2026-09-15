FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY service.py /app/service.py
USER 65532:65532
EXPOSE 8092
CMD ["uvicorn","service:app","--host","0.0.0.0","--port","8092","--workers","1"]

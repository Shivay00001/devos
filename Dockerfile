# DevOS - Python AI-native developer orchestration layer
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ai_engine/ ./ai_engine/
COPY run.py ./

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "run.py"]

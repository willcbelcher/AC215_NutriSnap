FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY src/deploy/vertex/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy only what the container needs: inference logic + serving app.
COPY backend /app/backend
COPY src/deploy/vertex /app/vertex

ENV PYTHONPATH=/app

CMD ["uvicorn", "vertex.app:app", "--host", "0.0.0.0", "--port", "8080"]


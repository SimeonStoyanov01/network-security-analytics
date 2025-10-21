FROM python:3.11-slim

WORKDIR /app

# Install system deps for typical Python packages
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY src/ /app/src/
WORKDIR /app/src

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]

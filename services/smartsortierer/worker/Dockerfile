# SmartSortierer Pro - Background Worker

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (tesseract optional for OCR)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 workeruser && chown -R workeruser:workeruser /app
USER workeruser

# Run worker
CMD ["python", "runner.py"]

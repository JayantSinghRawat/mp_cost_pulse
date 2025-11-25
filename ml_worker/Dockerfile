FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy training scripts
COPY train_*.py /app/

# Create models directory
RUN mkdir -p /app/models

# Note: Backend code is mounted as volume in docker-compose
# This allows training scripts to import from backend modules

# Default command
CMD ["python", "train_cost_predictor.py"]


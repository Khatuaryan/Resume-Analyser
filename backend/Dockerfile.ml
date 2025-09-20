# ML Models Microservice Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements for ML models
COPY requirements.txt .

# Install ML-specific dependencies
RUN pip install --no-cache-dir \
    scikit-learn==1.3.2 \
    xgboost==2.0.2 \
    lightgbm==4.1.0 \
    optuna==3.4.0 \
    pandas==2.1.4 \
    numpy==1.24.4 \
    joblib==1.3.2

# Copy ML service code
COPY services/ml_models.py .
COPY services/__init__.py .

# Create models directory
RUN mkdir -p models

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run ML service
CMD ["python", "-m", "uvicorn", "ml_models:app", "--host", "0.0.0.0", "--port", "8001"]

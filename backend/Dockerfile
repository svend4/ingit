# Backend Dockerfile
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libgit2-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ingit ./ingit

# Create non-root user
RUN useradd -m -u 1000 ingit && \
    chown -R ingit:ingit /app

USER ingit

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run application
CMD ["python", "-m", "ingit.main"]


# Development stage
FROM base as development

USER root
RUN pip install --no-cache-dir -r requirements-dev.txt
USER ingit

CMD ["python", "-m", "ingit.main"]


# Production stage
FROM base as production

ENV ENVIRONMENT=production
ENV API_RELOAD=false

CMD ["gunicorn", "ingit.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

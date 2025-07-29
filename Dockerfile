FROM python:3.10-slim

WORKDIR /app

# Install system requirements (minimal: only curl for healthcheck, no build-essential needed for this stack)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install with modern build tools
COPY requirements.txt .

# Upgrade pip/setuptools/wheel for best pip performance and compatibility
RUN pip install --upgrade pip setuptools wheel

# Main dependency installation
# Use legacy-resolver ONLY if getting pip "resolution-too-deep" error; otherwise, use regular install:
RUN pip install --use-deprecated=legacy-resolver -r requirements.txt

# Copy your application code
COPY main.py .

# Optionally add non-root user for extra security (optional, comment out if not desired)
#RUN groupadd -r appuser && useradd -r -g appuser appuser
#RUN chown -R appuser:appuser /app
#USER appuser

EXPOSE 8080

# Healthcheck using Python to avoid unnecessary curl dependency
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)"

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# Stage 1: Build and test
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies including test dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run tests
# RUN pytest --maxfail=1 --disable-warnings -q

# Stage 2: Production image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only application code (excluding tests)
COPY app ./app

# Expose application port
EXPOSE 8000

# Set the entry point for the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
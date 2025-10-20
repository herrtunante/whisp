# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /whisp

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire Whisp project
COPY .. /whisp/

# Set working directory to API folder
WORKDIR /whisp/api

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create results directory
RUN mkdir -p /whisp/results

# Expose port
EXPOSE 8000

# Set environment variable for Python path
ENV PYTHONPATH=/whisp:$PYTHONPATH

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

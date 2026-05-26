# Use the official lightweight Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
ENV FLASK_APP=main.py
ENV FLASK_CONFIG=development

# Install system dependencies: ffmpeg (for audio parsing), curl, and build utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install astral-uv package manager for fast, secure dependency installs
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install project dependencies directly into the system python
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application files
COPY . .

# Expose the application port
EXPOSE 10000

# Run Flask integrity checks (migrations/db sync) and start the server
CMD ["python", "main.py"]

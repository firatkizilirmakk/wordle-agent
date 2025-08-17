# Base image
FROM python:3.10-slim

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1

# Install Firefox ESR, wget, and other system dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    tar \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[api]"

# Copy the application code and necessary data files
COPY ./app ./app
COPY .env* ./

# Download and install geckodriver
# Check for the latest version: https://github.com/mozilla/geckodriver/releases
ARG GECKODRIVER_VERSION=v0.34.0
RUN wget "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" -O /tmp/geckodriver.tar.gz \
    && tar -C . -xzf /tmp/geckodriver.tar.gz \
    && rm /tmp/geckodriver.tar.gz \
    && chmod +x ./geckodriver

# Expose the port the app runs on
EXPOSE 8001

# The OPENAI_API_KEY must be passed as an environment variable at runtime.
# Example: docker run -e OPENAI_API_KEY='your_key_here' ...
# Do not hardcode your API key here.

# Command to run the FastAPI application
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8001"]

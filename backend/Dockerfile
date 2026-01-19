FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install system dependencies if any extra are needed
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Browsers
RUN playwright install chromium

# Copy App Code
COPY . .

# Expose Port
EXPOSE 8000

# Run Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

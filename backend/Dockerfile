FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# gcc used for building some python packages if needed (e.g. psutil, greenlet)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

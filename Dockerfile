FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install iputils-ping and curl for command injection lab diagnostics
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Initialize the SQLite database with initial dummy data & CTF flags
RUN python init_db.py

EXPOSE 5000

# Start Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "30", "app:app"]

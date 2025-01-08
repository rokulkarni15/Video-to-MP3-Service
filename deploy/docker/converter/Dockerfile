FROM python:3.9-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/converter.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p /tmp/uploads /tmp/converted \
    && chmod 777 /tmp/uploads \
    && chmod 777 /tmp/converted

# Copy source code
COPY src /app/src

CMD ["python", "-m", "src.converter.main"]
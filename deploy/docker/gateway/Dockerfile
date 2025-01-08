FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements/gateway.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p /tmp/uploads /tmp/converted \
    && chmod 777 /tmp/uploads \
    && chmod 777 /tmp/converted

# Copy source code
COPY src /app/src

CMD ["python", "-m", "src.gateway.main"]
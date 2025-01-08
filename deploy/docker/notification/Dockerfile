FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements/notification.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src /app/src

CMD ["python", "-m", "src.notification.main"]
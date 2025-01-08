# Video to MP3 Converter - Microservices Architecture

A microservices-based application that converts video files to MP3 format. Built with FastAPI, RabbitMQ, MongoDB, and MySQL.

## Architecture

The application consists of four microservices:
- **Auth Service**: Handles user authentication and authorization
- **Gateway Service**: Manages file uploads and API routing
- **Converter Service**: Processes video to MP3 conversion
- **Notification Service**: Handles email notifications

## Prerequisites

### For local development:
- Python 3.9+
- MySQL
- MongoDB
- RabbitMQ
- FFmpeg

### For Docker:
- Docker
- Docker Compose

## Local Setup

1. **Clone the repository**
```bash
git clone git@github.com:your-username/video-to-mp3.git
cd video-to-mp3
```
2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # For Unix/MacOS
# or
.\venv\Scripts\activate  # For Windows
```
3. **Install dependencies for each service**
```bash
pip install -r requirements/auth.txt
pip install -r requirements/gateway.txt
pip install -r requirements/converter.txt
pip install -r requirements/notification.txt
```
4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configurations
```
5. **Create required directories**
```bash
mkdir -p /tmp/uploads /tmp/converted
```
6. **Start the services (in separate terminals)**
```bash
# Auth Service
python -m src.auth.main

# Gateway Service
python -m src.gateway.main

# Converter Service
python -m src.converter.main

# Notification Service
python -m src.notification.main
```
## Docker Setup

1. **Clone the repository**
```bash
git clone git@github.com:your-username/video-to-mp3.git
cd video-to-mp3
```
2. **Set up environment variables**
```bash
git clone git@github.com:your-username/video-to-mp3.git
cd video-to-mp3
```
3. **Build and start services**
```bash
docker-compose up --build
```

## API Endpoints
### Auth Service
POST /api/v1/register - Register new user
POST /api/v1/token - Login and get token

### Gateway Service
POST /api/v1/convert - Upload video for conversion
GET /api/v1/status/{job_id} - Check conversion status
GET /api/v1/download/{job_id} - Download converted MP3

## Usage Example
1. Register a user
```bash
curl -X POST http://localhost:8001/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "testpass123"}'
```
2. Upload a video
```bash
curl -X POST http://localhost:8000/api/v1/convert \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@video.mp4"
```
3. Check Conversion Status
```bash
curl -X GET http://localhost:8000/api/v1/status/YOUR_JOB_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```



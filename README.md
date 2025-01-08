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

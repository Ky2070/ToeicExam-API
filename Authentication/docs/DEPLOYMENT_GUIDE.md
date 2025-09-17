# Deployment Guide - SSE Authentication System

## Overview

This guide covers the deployment of the Django REST Framework application with Server-Sent Events (SSE) authentication system. The system requires specific configuration for async support and real-time notifications.

## Prerequisites

- Docker and Docker Compose
- Redis server
- PostgreSQL database
- Python 3.8+
- ASGI server (Uvicorn, Daphne, or Hypercorn)

## Environment Configuration

### 1. Environment Variables

Create a `.env` file in your project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
DB_HOST=localhost
DB_PORT=5432
DB_NAME=toeic_api
DB_USER=postgres
DB_PASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redispass
REDIS_USE_SSL=false
REDIS_URL=redis://:redispass@localhost:6379/0

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
CORS_ALLOW_CREDENTIALS=true

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Security Settings
SECURE_SSL_REDIRECT=true
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=true
SECURE_CONTENT_TYPE_NOSNIFF=true
SECURE_BROWSER_XSS_FILTER=true
```

### 2. Docker Configuration

#### docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:13
    container_name: toeic_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "${DB_PORT}:5432"
    networks:
      - toeic_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: toeic_redis
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - toeic_network

  # Django Application
  web:
    build: .
    container_name: toeic_web
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             daphne -b 0.0.0.0 -p 8000 EnglishApp.asgi:application"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - toeic_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: toeic_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - toeic_network

networks:
  toeic_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=EnglishApp.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories
RUN mkdir -p staticfiles media

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "EnglishApp.asgi:application"]
```

### 3. Nginx Configuration

#### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server web:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # API endpoints with rate limiting
        location /api/v1/auth/login/ {
            limit_req zone=login burst=10 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # SSE endpoint - special configuration for long-lived connections
        location /api/v1/auth/sse/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # SSE specific settings
            proxy_set_header Connection '';
            proxy_http_version 1.1;
            proxy_buffering off;
            proxy_cache off;
            proxy_read_timeout 24h;
            proxy_send_timeout 24h;
        }

        # General API endpoints
        location /api/ {
            limit_req zone=api burst=120 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Admin interface
        location /admin/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health/ {
            proxy_pass http://django;
            access_log off;
        }
    }
}
```

## Deployment Steps

### 1. Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/your-repo/ToeicExam-API.git
cd ToeicExam-API

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Create SSL certificates (for production)
mkdir ssl
# Add your SSL certificates to ssl/ directory
```

### 3. Build and Deploy

```bash
# Build and start services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 4. Database Setup

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load initial data (if any)
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

## Monitoring and Logging

### 1. Health Checks

Create a health check endpoint:

```python
# health/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis

def health_check(request):
    try:
        # Database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Redis check
        cache.set('health_check', 'ok', 30)
        cache.get('health_check')
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

### 2. Logging Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'Authentication': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 3. Monitoring with Prometheus

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - toeic_network

  grafana:
    image: grafana/grafana
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - toeic_network

volumes:
  grafana_data:
```

## Scaling Considerations

### 1. Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  web:
    deploy:
      replicas: 3
    environment:
      - DJANGO_SETTINGS_MODULE=EnglishApp.settings.production
```

### 2. Load Balancing

Update Nginx configuration for multiple instances:

```nginx
upstream django {
    least_conn;
    server web_1:8000;
    server web_2:8000;
    server web_3:8000;
}
```

### 3. Session Affinity for SSE

For SSE connections, implement session affinity:

```nginx
upstream django_sse {
    ip_hash;  # Ensures same client goes to same server
    server web_1:8000;
    server web_2:8000;
    server web_3:8000;
}

location /api/v1/auth/sse/ {
    proxy_pass http://django_sse;
    # ... other SSE settings
}
```

## Security Hardening

### 1. Firewall Configuration

```bash
# UFW firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL/TLS Configuration

```bash
# Generate SSL certificate with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Security Updates

```bash
# Automated security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Backup Strategy

### 1. Database Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > backups/db_backup_$DATE.sql
find backups/ -name "db_backup_*.sql" -mtime +7 -delete
```

### 2. Media Files Backup

```bash
# Sync media files to S3
aws s3 sync /path/to/media s3://your-bucket/media/
```

## Troubleshooting

### Common Issues

1. **SSE Connections Dropping**
   - Check Nginx proxy timeout settings
   - Verify Redis connection stability
   - Monitor server memory usage

2. **High Memory Usage**
   - Monitor SSE connection count
   - Implement connection limits
   - Check for memory leaks in event handlers

3. **Database Connection Errors**
   - Verify connection pool settings
   - Check database server status
   - Monitor connection count

### Debugging Commands

```bash
# Check container logs
docker-compose logs -f web

# Access container shell
docker-compose exec web bash

# Monitor Redis connections
docker-compose exec redis redis-cli monitor

# Check database connections
docker-compose exec db psql -U $DB_USER -d $DB_NAME -c "SELECT * FROM pg_stat_activity;"
```

## Performance Optimization

### 1. Database Optimization

```python
# settings.py
DATABASES = {
    'default': {
        # ... other settings
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }
    }
}
```

### 2. Caching Strategy

```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}
```

### 3. Static File Optimization

```python
# Static files with CDN
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_CUSTOM_DOMAIN = 'your-cdn-domain.com'
```

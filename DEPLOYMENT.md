# Production Deployment Guide

## Overview
This guide covers deploying the Modular AI Architecture Visualization System v1.0 to production environments.

## Prerequisites

### System Requirements
- **Node.js**: v18.0.0 or higher
- **Python**: 3.9 or higher
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 1GB available space
- **Network**: Ports 80/443 for web access, custom ports for API

### Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## Deployment Options

### Option 1: Traditional Server Deployment

#### Backend Deployment
```bash
# 1. Set up Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False
export HOST=0.0.0.0
export PORT=5000

# 4. Run with production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend Deployment
```bash
# 1. Build for production
cd frontend
npm run build

# 2. Serve static files (choose one):

# Option A: Using nginx
sudo cp -r dist/* /var/www/html/

# Option B: Using Node.js serve
npm install -g serve
serve -s dist -l 3001

# Option C: Using Python
cd dist
python -m http.server 3001
```

### Option 2: Docker Deployment

#### Create Dockerfile for Backend
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### Create Dockerfile for Frontend
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

#### Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    volumes:
      - ./modules:/app/modules
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Option 3: Cloud Platform Deployment

#### Vercel (Frontend)
```json
// vercel.json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "YOUR_BACKEND_URL/api/$1" },
    { "src": "/(.*)", "dest": "/frontend/$1" }
  ]
}
```

#### Heroku (Backend)
```yaml
# Procfile
web: gunicorn app:app
release: python -c "print('Release phase')"
```

```json
# app.json
{
  "name": "modular-ai-architecture-backend",
  "description": "Backend API for Modular AI Architecture System",
  "keywords": ["python", "flask", "api"],
  "env": {
    "FLASK_ENV": {
      "description": "Flask environment",
      "value": "production"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    }
  }
}
```

## Configuration

### Environment Variables
```bash
# Backend (.env)
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-here
CORS_ORIGINS=https://yourdomain.com
MODULE_PATH=/app/modules
LOG_LEVEL=INFO

# Frontend (built into application)
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_TITLE="Modular AI Architecture"
```

### Nginx Configuration
```nginx
# nginx.conf
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # API Proxy
    location /api/ {
        proxy_pass http://backend:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Security Considerations

### Production Security Checklist
- [ ] Use HTTPS/TLS certificates (Let's Encrypt recommended)
- [ ] Set secure session cookies
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Set up logging and monitoring
- [ ] Regular security updates
- [ ] Backup strategy for module data

### HTTPS Setup with Let's Encrypt
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Application Monitoring
```python
# Add to app.py for production monitoring
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
```

### Health Check Endpoints
```python
# Add to app.py
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })
```

## Performance Optimization

### Frontend Optimizations
- Gzip compression enabled
- Asset caching (1 year for static assets)
- Bundle size: ~794KB (already optimized)
- CDN recommended for global users

### Backend Optimizations
- Use Gunicorn with multiple workers
- Enable connection pooling if using database
- Implement caching for frequent requests
- Monitor memory usage

## Backup and Recovery

### Data Backup Strategy
```bash
#!/bin/bash
# backup_modules.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "backups/modules_backup_$DATE.tar.gz" modules/
find backups/ -name "modules_backup_*.tar.gz" -mtime +7 -delete
```

### Recovery Procedures
1. Stop application services
2. Restore module files from backup
3. Restart services
4. Verify application health

## Troubleshooting

### Common Issues
1. **Port conflicts**: Use `./kill_ports.sh` and check port availability
2. **Module loading errors**: Verify YAML syntax and file permissions
3. **CORS issues**: Check frontend-backend URL configuration
4. **Memory issues**: Monitor resource usage and scale appropriately

### Debug Mode
```bash
# Enable debug logging temporarily
export LOG_LEVEL=DEBUG
# Restart application
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Multiple backend instances
- Shared storage for modules directory
- Session stickiness not required (stateless API)

### Vertical Scaling
- Monitor CPU/Memory usage
- Increase worker processes as needed
- Optimize database queries if database is added

## Post-Deployment Verification

### Verification Checklist
- [ ] Frontend loads correctly
- [ ] API endpoints respond
- [ ] Module visualization works
- [ ] Search functionality works
- [ ] Export features work
- [ ] Error handling works
- [ ] Performance is acceptable
- [ ] Security headers are set
- [ ] Logging is working
- [ ] Backups are configured

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 http://yourdomain.com/api/modules

# Test frontend
ab -n 100 -c 5 http://yourdomain.com/
```

## Support and Maintenance

### Regular Maintenance Tasks
- Weekly: Review logs for errors
- Monthly: Update dependencies
- Quarterly: Security audit
- Yearly: Major version updates

### Getting Help
- Check application logs first
- Review this deployment guide
- Create GitHub issue with reproduction steps
- Include environment details and error messages
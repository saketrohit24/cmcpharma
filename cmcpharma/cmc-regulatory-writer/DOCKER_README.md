# 🐳 Docker Deployment Guide for CMC Regulatory Writer

This guide explains how to containerize and deploy the CMC Regulatory Writer application using Docker.

## 📋 Prerequisites

- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **LLM API Key** (NVIDIA API key for Moonshot AI Kimi)

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
# Navigate to project root
cd cmc-regulatory-writer

# Copy environment template
cp .env.docker .env

# Edit .env with your API keys
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file:

```bash
# Required: Your NVIDIA API key for Moonshot AI Kimi
LLM_API_KEY=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

# Optional: Additional NVIDIA API key
NVIDIA_API_KEY=your_nvidia_api_key_here

# Database (SQLite by default)
DATABASE_URL=sqlite:///./app.db
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   (React/Vite)  │────│   (FastAPI)     │
│   Port: 80      │    │   Port: 8001    │
│   Nginx         │    │   Python 3.11   │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                Docker Network
```

## 📁 Docker Files Structure

```
cmc-regulatory-writer/
├── docker-compose.yml          # Development setup
├── docker-compose.prod.yml     # Production setup
├── .env.docker                 # Environment template
├── backend/
│   ├── Dockerfile             # Backend container
│   └── .dockerignore          # Backend ignore rules
├── frontend/
│   ├── Dockerfile             # Frontend container
│   ├── nginx.conf             # Nginx configuration
│   └── .dockerignore          # Frontend ignore rules
└── DOCKER_README.md           # This file
```

## 🛠️ Development vs Production

### Development (Default)

```bash
# Development with live reload and port mapping
docker-compose up --build

# Services:
# - Frontend: http://localhost:80
# - Backend: http://localhost:8001
# - Volumes mounted for development
```

### Production

```bash
# Production with optimized settings
docker-compose -f docker-compose.prod.yml up -d --build

# Features:
# - Resource limits
# - Named volumes
# - Health checks
# - Restart policies
```

## 🔧 Common Commands

### Build and Management

```bash
# Build only (without starting)
docker-compose build

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
docker-compose logs backend
docker-compose logs frontend

# Restart service
docker-compose restart backend
```

### Maintenance

```bash
# Clean up containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean up system
docker system prune -a
```

## 📊 Service Configuration

### Backend Service

- **Image**: Python 3.11 slim
- **Port**: 8001
- **Health Check**: `/api/health`
- **Volumes**: 
  - `persistent_uploads/` - Document storage
  - `temp_exports/` - Export cache

### Frontend Service

- **Image**: Node 18 + Nginx Alpine
- **Port**: 80
- **Features**:
  - Gzip compression
  - SPA routing support
  - API proxy to backend
  - Static asset caching

## 🔒 Security Considerations

### Production Checklist

1. **Environment Variables**
   ```bash
   # Use secure API keys
   LLM_API_KEY=your_secure_api_key
   
   # Add secret keys for production
   SECRET_KEY=your_secret_key
   JWT_SECRET_KEY=your_jwt_secret
   ```

2. **Network Security**
   ```bash
   # Run on internal network
   docker network create cmc-secure-network
   ```

3. **HTTPS Setup** (Production)
   ```bash
   # Add SSL certificates
   # Update nginx.conf for SSL termination
   # Use docker-compose.prod.yml
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :80
   lsof -i :8001
   
   # Kill processes or change ports in docker-compose.yml
   ```

2. **API Key Issues**
   ```bash
   # Check environment variables
   docker-compose exec backend env | grep LLM_API_KEY
   
   # Restart after changing .env
   docker-compose restart backend
   ```

3. **Build Failures**
   ```bash
   # Clean build cache
   docker-compose build --no-cache
   
   # Check Docker logs
   docker-compose logs backend
   ```

4. **Memory Issues**
   ```bash
   # Increase Docker memory limits
   # Check system resources
   docker stats
   ```

### Health Checks

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8001/api/health
curl http://localhost/

# Check logs for errors
docker-compose logs --tail=50 backend
```

## 📈 Performance Optimization

### Resource Limits

Edit `docker-compose.prod.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
```

### Volume Optimization

```yaml
volumes:
  # Use named volumes for better performance
  backend_uploads:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Or rolling update
docker-compose up -d --force-recreate --build
```

### Backup and Restore

```bash
# Backup volumes
docker run --rm -v cmc_backend_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz /data

# Restore volumes  
docker run --rm -v cmc_backend_uploads:/data -v $(pwd):/backup alpine tar xzf /backup/uploads-backup.tar.gz -C /
```

## 🆘 Support

For issues related to:
- **Docker setup**: Check this guide and Docker logs
- **Application bugs**: See main README.md
- **API errors**: Check backend logs and API documentation

---

**🎉 You're ready to deploy CMC Regulatory Writer with Docker!**
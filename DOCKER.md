# 🐳 Docker Deployment Guide

## Quick Start

### 1. Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)

### 2. Setup Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 3. Build and Run
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Docker Files Overview

### Project Structure
```
Jobs/
├── docker-compose.yml       # Orchestrates all services
├── .env.example            # Environment template
│
├── backend/
│   ├── Dockerfile          # Backend container
│   └── .dockerignore       # Ignore patterns
│
└── frontend/
    ├── Dockerfile          # Frontend container
    ├── nginx.conf          # Nginx configuration
    └── .dockerignore       # Ignore patterns
```

---

## Services

### Backend Service
- **Image**: Python 3.13 slim
- **Port**: 8000
- **Features**:
  - FastAPI application
  - Playwright for web scraping
  - SQLite database
  - ChromaDB vector store
  - Health checks

### Frontend Service
- **Image**: Node 20 (build) + Nginx Alpine (serve)
- **Port**: 80
- **Features**:
  - React application
  - Optimized production build
  - Nginx reverse proxy
  - API proxy to backend
  - Static asset caching

---

## Docker Commands

### Development
```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend
```

### Maintenance
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache

# Remove unused images
docker system prune -a
```

### Debugging
```bash
# Execute command in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# View container stats
docker stats

# Inspect container
docker-compose ps
docker inspect job-portal-backend
```

---

## Data Persistence

### Volumes
```yaml
volumes:
  - ./backend/data:/app/data          # SQLite database
  - ./backend/chroma_db:/app/chroma_db  # Vector database
```

**Data is persisted** on your host machine in:
- `backend/data/` - Job database
- `backend/chroma_db/` - Vector embeddings

---

## Environment Variables

### Required
```bash
RAPIDAPI_KEY=xxx        # JSearch API key
RAPIDAPI_HOST=xxx       # JSearch API host
ADZUNA_APP_ID=xxx       # Adzuna app ID
ADZUNA_APP_KEY=xxx      # Adzuna app key
```

### Optional
```bash
DATABASE_URL=sqlite:///data/jobs.db
CHROMA_SERVER_HOST=localhost
CHROMA_SERVER_PORT=8000
```

---

## Production Deployment

### 1. Build for Production
```bash
docker-compose -f docker-compose.yml build
```

### 2. Deploy to Server
```bash
# Copy files to server
scp -r . user@server:/path/to/app

# SSH into server
ssh user@server

# Start services
cd /path/to/app
docker-compose up -d
```

### 3. Setup Reverse Proxy (Optional)
Use Nginx or Traefik to:
- Add HTTPS/SSL
- Custom domain
- Load balancing

---

## Health Checks

Both services include health checks:

### Backend
```bash
curl http://localhost:8000/health
```

### Frontend
```bash
curl http://localhost/
```

---

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend
  - "8080:80"    # Frontend
```

### Permission Issues
```bash
# Fix data directory permissions
chmod -R 755 backend/data
chmod -R 755 backend/chroma_db
```

### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose build --no-cache backend
docker-compose up backend
```

### Database Issues
```bash
# Reset database
rm -rf backend/data/*.db
docker-compose restart backend
```

---

## Performance Optimization

### Multi-stage Builds
- Frontend uses multi-stage build (Node → Nginx)
- Reduces final image size by ~90%

### Caching
- Layer caching for faster rebuilds
- Nginx caches static assets
- Docker build cache optimization

### Resource Limits
Add to docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build images
        run: docker-compose build
      - name: Run tests
        run: docker-compose run backend pytest
```

---

## Security Best Practices

1. ✅ **Use .env for secrets** (never commit .env)
2. ✅ **Non-root user** in containers
3. ✅ **Health checks** enabled
4. ✅ **Security headers** in Nginx
5. ✅ **Minimal base images** (Alpine, Slim)
6. ✅ **No sensitive data** in images

---

## Next Steps

1. **Setup monitoring**: Add Prometheus + Grafana
2. **Add logging**: Centralized logging with ELK stack
3. **Implement CI/CD**: Automated builds and deployments
4. **Scale horizontally**: Use Docker Swarm or Kubernetes

---

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Rebuild: `docker-compose build --no-cache`
- Reset: `docker-compose down -v && docker-compose up -d`

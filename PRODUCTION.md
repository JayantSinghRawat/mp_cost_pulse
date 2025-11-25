# Production Deployment Guide

## Overview

MP Cost Pulse is a production-ready, market-grade SaaS platform with full ML integration, authentication, and scalable architecture.

## Architecture

```
┌─────────────┐
│   Nginx     │  Port 80 (Reverse Proxy)
└──────┬──────┘
       │
   ┌───┴───┬──────────┬──────────┐
   │       │          │          │
┌──▼──┐ ┌──▼──┐  ┌───▼───┐  ┌───▼────┐
│Front│ │Back │  │ML     │  │Airflow │
│end  │ │end  │  │Worker │  │        │
└──┬──┘ └──┬──┘  └───┬───┘  └───┬────┘
   │       │          │          │
   └───────┴──────────┴──────────┘
              │
         ┌────▼────┐
         │Postgres │
         │+PostGIS │
         └─────────┘
```

## Services

1. **Nginx**: Reverse proxy, load balancing, SSL termination
2. **Frontend**: React SPA (production build)
3. **Backend**: FastAPI with 4 workers
4. **ML Worker**: Model training service
5. **PostgreSQL**: Database with PostGIS
6. **Airflow**: Scheduled data scraping

## Deployment Steps

### 1. Environment Setup

Create `.env` file:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=mpcostpulse
SECRET_KEY=your-very-secure-secret-key-here
MAPBOX_ACCESS_TOKEN=your_token
ISOCRONE_API_KEY=your_key
BIGBASKET_API_KEY=your_key
BLINKIT_API_KEY=your_key
CORS_ORIGINS=["http://yourdomain.com","https://yourdomain.com"]
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Initialize Database

Database is auto-initialized, but you can verify:
```bash
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
```

### 4. Train ML Models

```bash
# Train cost predictor
docker-compose exec ml-worker python train_cost_predictor.py

# Train rent classifier (optional - uses pretrained DistilBERT)
docker-compose exec ml-worker python train_rent_classifier.py
```

### 5. Verify Services

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs -f

# Test endpoints
curl http://localhost/health
curl http://localhost/api/v1/health
```

## Production Optimizations

### Backend
- Uses 4 Uvicorn workers for concurrency
- Connection pooling (10 base, 20 overflow)
- Health checks enabled
- Auto-restart on failure

### Frontend
- Production build with Vite
- Gzip compression
- Static asset caching (1 year)
- SPA routing support

### Nginx
- Reverse proxy for all services
- Security headers
- Gzip compression
- Request timeouts configured

### ML Models
- Models stored in shared volume
- Version tracking in database
- Automatic fallback if models unavailable

## Scaling

### Horizontal Scaling
```bash
# Scale backend workers
docker-compose up -d --scale backend=5

# Update Nginx upstream configuration for load balancing
```

### Vertical Scaling
- Increase Docker memory allocation
- Adjust database connection pool
- Tune Uvicorn workers based on CPU cores

## Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS origins properly
- [ ] Enable HTTPS (add SSL certificates)
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] API rate limiting (add if needed)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (SQLAlchemy handles this)

## Monitoring

### Health Checks
- Backend: `GET /health`
- Database: PostgreSQL health check
- Frontend: Nginx status

### Logs
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ml-worker
```

### Metrics
- Database connections
- API response times
- Model prediction latency
- Error rates

## Backup & Recovery

### Database Backup
```bash
docker-compose exec postgres pg_dump -U postgres mpcostpulse > backup.sql
```

### Model Backup
```bash
docker-compose exec ml-worker tar -czf models_backup.tar.gz /app/models
```

### Restore
```bash
# Database
docker-compose exec -T postgres psql -U postgres mpcostpulse < backup.sql

# Models
docker-compose exec ml-worker tar -xzf models_backup.tar.gz -C /app
```

## Troubleshooting

### Services won't start
- Check Docker resources (memory, CPU)
- Verify .env file exists
- Check port conflicts

### ML models not loading
- Verify models directory exists
- Check model files are present
- Review ML worker logs

### Database connection errors
- Verify PostgreSQL is healthy
- Check DATABASE_URL in .env
- Review connection pool settings

### Frontend not loading
- Check Nginx configuration
- Verify frontend build succeeded
- Check browser console for errors

## Performance Tuning

1. **Database**: Add indexes on frequently queried columns
2. **Caching**: Implement Redis for API response caching
3. **CDN**: Use CDN for static assets
4. **Model Optimization**: Quantize PyTorch models for faster inference
5. **Connection Pooling**: Tune based on traffic

## Support

For production issues, check:
1. Service logs: `docker-compose logs [service]`
2. Health endpoints: `/health`, `/api/v1/health`
3. Database status: `docker-compose exec postgres pg_isready`


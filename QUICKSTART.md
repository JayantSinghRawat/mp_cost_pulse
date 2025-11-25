# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Start All Services
```bash
docker-compose up -d
```

### 2. Wait for Services to Initialize
```bash
# Check status
docker-compose ps

# Watch logs
docker-compose logs -f
```

### 3. Access the Application
- **Main App (via Nginx)**: http://localhost
- **Frontend (direct)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📝 First Time Setup

1. **Register an Account**
   - Go to http://localhost/login
   - Click "Register"
   - Fill in your details and create account

2. **Train ML Models (Optional)**
   ```bash
   docker-compose exec ml-worker python train_cost_predictor.py
   ```

3. **Explore Features**
   - Dashboard: View heatmaps and inflation trends
   - Cost Prediction: Get personalized cost estimates
   - Locality Comparison: Compare different areas
   - Cost Burden Index: See affordability metrics

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart [service-name]

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Access database
docker-compose exec postgres psql -U postgres -d mpcostpulse

# Run ML training
docker-compose exec ml-worker python train_cost_predictor.py
```

## 🐛 Troubleshooting

**Services not starting?**
- Check Docker has enough resources (8GB RAM recommended)
- Verify ports 80, 3000, 8000, 5432, 8080 are available

**Can't register/login?**
- Check backend logs: `docker-compose logs backend`
- Verify database is running: `docker-compose ps postgres`

**ML predictions not working?**
- Train the models first (see above)
- Check ML worker logs: `docker-compose logs ml-worker`

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Check [PRODUCTION.md](PRODUCTION.md) for production deployment
- Explore API docs at http://localhost:8000/docs


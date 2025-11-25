# How to Access MP Cost Pulse

## 🚀 Quick Access Steps

### Step 1: Start All Services
```bash
cd /Users/jayant/Documents/heatmap
docker-compose up -d
```

Wait about 30-60 seconds for all services to start.

### Step 2: Check Service Status
```bash
docker-compose ps
```

All services should show "Up" status.

### Step 3: Access the Application

#### Option A: Via Nginx (Recommended - Port 80)
```
http://localhost
```
This is the main entry point through the reverse proxy.

#### Option B: Direct Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 4: Register Your First Account

1. **Open your browser** and go to:
   ```
   http://localhost/login
   ```
   or
   ```
   http://localhost:3000/login
   ```

2. **Click the "Register" tab**

3. **Fill in the form**:
   - Full Name: Your name
   - Email: your@email.com
   - Username: choose a username
   - Password: choose a password

4. **Click "Sign Up"**

5. **You'll be automatically logged in** and redirected to the dashboard!

### Step 5: Explore Features

Once logged in, you can:

1. **Dashboard** (`/`)
   - View locality heatmaps
   - See inflation trends
   - Explore cost data

2. **Cost Prediction** (`/profile`)
   - Fill in your profile (income, family size, etc.)
   - Select a locality
   - Get personalized cost predictions

3. **Locality Comparison** (`/comparison`)
   - Compare costs across different localities
   - See detailed breakdowns

4. **Cost Burden Index** (`/cost-burden`)
   - Visualize affordability metrics
   - See cost burden heatmaps

## 🔍 Verify Everything is Working

### Check Backend
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

### Check Frontend
Open http://localhost:3000 in your browser - you should see the login page.

### Check Database
```bash
docker-compose exec postgres psql -U postgres -d mpcostpulse -c "SELECT COUNT(*) FROM users;"
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🐛 Troubleshooting

### Can't Access http://localhost
**Check if services are running:**
```bash
docker-compose ps
```

**If services are down, start them:**
```bash
docker-compose up -d
```

**Check for errors:**
```bash
docker-compose logs backend | tail -30
docker-compose logs frontend | tail -30
```

### Port Already in Use
If you get "port already in use" errors:
```bash
# Stop conflicting services or change ports in docker-compose.yml
docker-compose down
# Edit docker-compose.yml to change ports if needed
docker-compose up -d
```

### Database Connection Errors
```bash
# Restart database
docker-compose restart postgres

# Wait for it to be healthy
docker-compose ps postgres
```

### Frontend Not Loading
```bash
# Rebuild frontend
docker-compose up -d --build frontend

# Check frontend logs
docker-compose logs frontend
```

### Can't Register/Login
```bash
# Check backend logs
docker-compose logs backend | grep -i error

# Verify database has users table
docker-compose exec postgres psql -U postgres -d mpcostpulse -c "\d users"
```

## 📱 Access URLs Summary

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost | Via Nginx (recommended) |
| **Frontend** | http://localhost:3000 | Direct access |
| **Backend API** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Health** | http://localhost:8000/health | Health check |
| **Airflow** | http://localhost:8080 | Airflow UI |

## 🎯 First Time Setup Checklist

- [ ] Services started: `docker-compose ps` shows all "Up"
- [ ] Backend healthy: `curl http://localhost:8000/health` returns OK
- [ ] Frontend accessible: http://localhost:3000 loads
- [ ] Registered account: Created user account
- [ ] Logged in: Can see dashboard
- [ ] (Optional) Trained ML models: `docker-compose exec ml-worker python train_cost_predictor.py`

## 🚀 Next Steps After Access

1. **Train ML Models** (for better predictions):
   ```bash
   docker-compose exec ml-worker python train_cost_predictor.py
   ```

2. **Add Some Data**:
   - Use the scraping endpoints to add rent listings
   - Or manually add data via API

3. **Explore API**:
   - Visit http://localhost:8000/docs
   - Try out different endpoints
   - Test ML predictions

4. **Customize**:
   - Add your API keys in `.env` file
   - Configure CORS origins
   - Set production SECRET_KEY

## 💡 Pro Tips

- **Use Nginx URL** (http://localhost) for production-like experience
- **Check API docs** at `/docs` to see all available endpoints
- **Monitor logs** with `docker-compose logs -f` for debugging
- **Use browser DevTools** to see API calls and errors

---

**Ready to go!** Open http://localhost in your browser and start exploring! 🎉


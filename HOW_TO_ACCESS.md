# 🚀 How to Access MP Cost Pulse

## ✅ Quick Access (3 Steps)

### Step 1: Make Sure Services Are Running
```bash
cd /Users/jayant/Documents/heatmap
docker-compose ps
```

All services should show "Up" status. If not, start them:
```bash
docker-compose up -d
```

### Step 2: Wait for Services to Initialize
Wait about 30-60 seconds for all services to fully start.

### Step 3: Open in Your Browser

**🎯 Main Entry Point (Recommended):**
```
http://localhost
```
This goes through Nginx reverse proxy.

**OR Direct Access:**
```
http://localhost:3000
```
This is the frontend directly.

---

## 📱 Access URLs

| What You Want | URL | Notes |
|---------------|-----|-------|
| **Main Application** | http://localhost | Via Nginx (best) |
| **Frontend Direct** | http://localhost:3000 | React dev server |
| **Backend API** | http://localhost:8000 | Direct API (if ports exposed) |
| **API Documentation** | http://localhost:8000/docs | Swagger UI |
| **Health Check** | http://localhost:8000/health | Backend status |

---

## 🔐 First Time: Register & Login

1. **Open Browser**: Go to http://localhost or http://localhost:3000

2. **You'll see the Login Page**

3. **Click "Register" tab**

4. **Fill in the form**:
   - Full Name: Your name
   - Email: your@email.com  
   - Username: choose a username
   - Password: choose a password

5. **Click "Sign Up"**

6. **You're in!** You'll be automatically logged in and see the dashboard.

---

## 🎯 What You Can Do After Login

### 1. Dashboard (`/`)
- View locality heatmaps
- See inflation trends
- Explore cost data visualizations

### 2. Cost Prediction (`/profile`)
- Fill in your profile:
  - Monthly income
  - Family size
  - Property preference (1BHK/2BHK/3BHK)
  - Commute details
  - Amenities priority
- Select a locality
- Get AI-powered cost prediction!

### 3. Locality Comparison (`/comparison`)
- Select up to 5 localities
- Compare costs side-by-side
- See detailed breakdowns

### 4. Cost Burden Index (`/cost-burden`)
- Visualize affordability
- See cost burden heatmaps
- Click on localities for details

---

## 🔍 Verify Everything Works

### Check if Backend is Running
```bash
docker-compose exec backend curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

### Check if Frontend is Running
Open http://localhost:3000 in browser - should see login page

### Check Service Status
```bash
docker-compose ps
```
All should show "Up"

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 🐛 Troubleshooting

### "Can't connect to localhost"
**Solution:**
```bash
# Check if services are running
docker-compose ps

# If not running, start them
docker-compose up -d

# Wait 30 seconds, then try again
```

### "502 Bad Gateway" or "Connection Refused"
**Solution:**
```bash
# Restart services
docker-compose restart

# Check backend logs
docker-compose logs backend | tail -30

# Check if backend is healthy
docker-compose exec backend curl http://localhost:8000/health
```

### "Can't Register/Login"
**Solution:**
```bash
# Check backend logs for errors
docker-compose logs backend | grep -i error

# Verify database is running
docker-compose ps postgres

# Restart backend
docker-compose restart backend
```

### Frontend Shows Blank Page
**Solution:**
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

---

## 💡 Pro Tips

1. **Use http://localhost** (port 80) - This is the production-like setup with Nginx
2. **Check browser console** (F12) for any JavaScript errors
3. **Check Network tab** to see API calls
4. **Use API docs** at http://localhost:8000/docs to test endpoints directly

---

## 🎓 Next Steps

1. **Train ML Models** (for better predictions):
   ```bash
   docker-compose exec ml-worker python train_cost_predictor.py
   ```

2. **Explore API**:
   - Visit http://localhost:8000/docs
   - Try different endpoints
   - Test authentication

3. **Add Data**:
   - Use scraping endpoints
   - Or add data manually via API

---

## ✅ Quick Checklist

- [ ] Services running: `docker-compose ps` shows all "Up"
- [ ] Can access: http://localhost loads
- [ ] Can register: Create account successfully  
- [ ] Can login: Log in with your account
- [ ] Can see dashboard: After login, see main page
- [ ] (Optional) ML models trained: Run training script

---

**🎉 You're all set!** Open http://localhost in your browser and start using MP Cost Pulse!


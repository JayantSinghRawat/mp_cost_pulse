# 🗺️ Setup Google Maps API

## Quick Setup (3 Steps)

### Step 1: Get Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Places API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Places API"
   - Click "Enable"
4. Create API Key:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key
   - (Optional) Restrict the key to "Places API" for security

### Step 2: Set the API Key

**Option A: Using .env file (Recommended)**
```bash
# Create .env file in project root
echo "GOOGLE_PLACES_API_KEY=your-api-key-here" > .env
```

**Option B: Export as environment variable**
```bash
export GOOGLE_PLACES_API_KEY=your-api-key-here
```

**Option C: Add directly to docker-compose.yml**
```yaml
environment:
  GOOGLE_PLACES_API_KEY: "your-api-key-here"
```

### Step 3: Restart and Refresh Data

```bash
# Restart backend to load the API key
docker-compose restart backend

# Wait a few seconds for backend to start
sleep 5

# Refresh all Bhopal neighborhoods with Google Maps data
docker-compose exec backend python refresh_bhopal_places_data.py
```

## ✅ Verify It's Working

Check if Google Places API is being used:
```bash
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT l.name, nd.restaurants_count, nd.grocery_stores_count, \
          nd.hospitals_count, nd.schools_count, nd.parks_count, nd.shopping_malls_count, \
          nd.data_source->>'amenities_source' as source \
   FROM neighborhood_data nd JOIN localities l ON nd.locality_id = l.id \
   WHERE l.city = 'Bhopal';"
```

You should see:
- `source` = `google_places` ✅
- Realistic counts (not just 0 or 1)
- Restaurant data populated

## 📊 What You'll Get

With Google Maps API enabled, you'll get **real data** for:

- 🍽️ **Restaurants**: Count, average ratings, highly-rated restaurants
- 🛒 **Grocery Stores**: Count and locations
- 🏥 **Hospitals**: Accurate count
- 🏫 **Schools**: Accurate count
- 🌳 **Parks**: Accurate count
- 🛍️ **Malls**: Accurate count

## 💰 Cost

- **Free Tier**: $200/month credit from Google
- **Places API Nearby Search**: $32 per 1000 requests
- For 5 localities × 6 place types = ~30 requests per refresh
- **Very affordable** - well within free tier!

## 🔄 Refresh Data Anytime

To get latest data:
```bash
docker-compose exec backend python refresh_bhopal_places_data.py
```

## 🐛 Troubleshooting

**If you see `openstreetmap` as source:**
- API key not set correctly
- Check: `docker-compose exec backend python -c "from app.core.config import settings; print('Key:', 'SET' if settings.GOOGLE_PLACES_API_KEY else 'NOT SET')"`
- Restart backend after setting key

**If counts are still 0:**
- Verify API key is valid
- Check Google Cloud Console for API usage/errors
- Ensure Places API is enabled in your project

## 📝 Example .env File

Create `.env` in project root:
```env
GOOGLE_PLACES_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Then restart:
```bash
docker-compose restart backend
```


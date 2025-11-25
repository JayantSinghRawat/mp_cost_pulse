# Google Places API Setup

## 🗺️ Using Google Maps API for Real Data

The system now uses **Google Places API** to fetch real data for:
- 🍽️ **Restaurants** (count, ratings, highly-rated)
- 🛒 **Grocery Stores** (count, locations)
- 🏥 **Hospitals** (count)
- 🏫 **Schools** (count)
- 🌳 **Parks** (count)
- 🛍️ **Malls** (count)

## ⚙️ Setup Instructions

### 1. Get Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Places API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Places API"
   - Click "Enable"
4. Create API Key:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key

### 2. Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
export GOOGLE_PLACES_API_KEY="your-api-key-here"
```

**Option B: Docker Compose**
Add to `docker-compose.yml`:
```yaml
services:
  backend:
    environment:
      - GOOGLE_PLACES_API_KEY=your-api-key-here
```

**Option C: .env File**
Create `.env` file in `backend/`:
```
GOOGLE_PLACES_API_KEY=your-api-key-here
```

### 3. Restart Services
```bash
docker-compose restart backend
```

### 4. Refresh Data
```bash
docker-compose exec backend python refresh_bhopal_places_data.py
```

## 🔄 Fallback to OpenStreetMap

If Google Places API key is **not set**, the system automatically uses:
- **OpenStreetMap (Overpass API)** - Free, no key required
- Provides basic counts for hospitals, schools, parks
- Less detailed than Google Places but still functional

## 📊 Current Status

Check if Google Places API is being used:
```bash
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT l.name, nd.data_source->>'amenities_source' as source \
   FROM neighborhood_data nd JOIN localities l ON nd.locality_id = l.id \
   WHERE l.city = 'Bhopal';"
```

- `google_places` = Using Google Places API ✅
- `openstreetmap` = Using OpenStreetMap (fallback) ⚠️

## 🎯 Benefits of Google Places API

1. **More Accurate**: Real-time data from Google Maps
2. **More Complete**: Better coverage than OpenStreetMap
3. **Restaurant Ratings**: Actual ratings and reviews
4. **Grocery Stores**: Detailed store information
5. **Better Counts**: More accurate counts for all amenities

## 💰 Cost

- **Free Tier**: $200/month credit
- **Places API Nearby Search**: $32 per 1000 requests
- For 5 localities × 6 place types = 30 requests per refresh
- **Very affordable** for this use case

## 🔍 Verify Data

After setting up, check the data:
```bash
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT l.name, nd.restaurants_count, nd.grocery_stores_count, \
          nd.hospitals_count, nd.schools_count, nd.parks_count, nd.shopping_malls_count \
   FROM neighborhood_data nd JOIN localities l ON nd.locality_id = l.id \
   WHERE l.city = 'Bhopal';"
```

You should see **realistic counts** (not just 0 or 1) when using Google Places API!


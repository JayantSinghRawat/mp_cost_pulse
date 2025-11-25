# Testing Guide for MP Cost Pulse

## Quick Test Checklist

### 1. **Test Frontend - Neighborhood Recommendations**

1. Open the application: http://localhost (or http://localhost:80)
2. Navigate to "Find Neighborhood" page
3. Test different cities:
   - Select "Indore" from the city dropdown
   - Set budget: ₹30,000
   - Click "Get Recommendations"
   - Verify recommendations appear
   - Repeat for other cities: Gwalior, Jabalpur, Ujjain

4. Verify Food & Grocery Data Display:
   - Check if "Food & Beverages" section appears
   - Verify restaurant count and ratings are shown
   - Check grocery stores count
   - Verify grocery cost is displayed

### 2. **Test Backend APIs**

#### Test Recommendations API
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/neighborhoods" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Indore",
    "number_of_people": 2,
    "max_travel_distance_km": 5,
    "budget": 30000,
    "property_type": "2BHK",
    "top_n": 5
  }' | python3 -m json.tool
```

#### Test Localities API
```bash
# Get all localities
curl "http://localhost:8000/api/v1/geospatial/localities" | python3 -m json.tool

# Get localities for a specific city
curl "http://localhost:8000/api/v1/geospatial/localities?city=Indore" | python3 -m json.tool
```

#### Test Grocery API
```bash
# Get grocery stores for a locality
curl "http://localhost:8000/api/v1/groceries/stores?locality_id=1" | python3 -m json.tool

# Calculate grocery cost
curl "http://localhost:8000/api/v1/groceries/cost/1" | python3 -m json.tool
```

### 3. **Test ML Model**

```bash
# Test the trained model
docker-compose exec ml-worker python test_model.py
```

### 4. **Verify Data from Public APIs**

#### Check Database
```bash
# Check localities by city
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT city, COUNT(*) FROM localities GROUP BY city;"

# Check neighborhood data
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT city, COUNT(*), AVG(avg_grocery_cost_monthly), AVG(restaurants_count) \
   FROM neighborhood_data GROUP BY city;"
```

#### Check ML Training Logs
```bash
docker-compose logs ml-worker --tail=100 | grep -E "(REAL|Fetching|Training|completed)"
```

### 5. **Test Data Refresh**

```bash
# Refresh neighborhood data for a city
curl -X POST "http://localhost:8000/api/v1/recommendations/refresh/Indore" | python3 -m json.tool
```

## Automated Test Script

Run the comprehensive test script:
```bash
./test_all.sh
```


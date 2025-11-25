# Quick Testing Guide

## 🚀 Quick Start Testing

### 1. **Frontend Testing (Visual)**

1. **Open the application:**
   ```
   http://localhost
   ```

2. **Test Neighborhood Recommendations:**
   - Go to "Find Neighborhood" page
   - Select different cities from dropdown:
     - Bhopal
     - Indore
     - Gwalior
     - Jabalpur
     - Ujjain
   - Set your preferences and click "Get Recommendations"
   - **Verify:**
     - ✅ Recommendations appear
     - ✅ Food & Beverages section shows restaurant data
     - ✅ Grocery cost is displayed
     - ✅ Grocery stores count is shown

### 2. **API Testing (Command Line)**

#### Test Recommendations for Different Cities:
```bash
# Test Indore
curl -X POST "http://localhost:8000/api/v1/recommendations/neighborhoods" \
  -H "Content-Type: application/json" \
  -d '{"city": "Indore", "number_of_people": 2, "max_travel_distance_km": 5, "budget": 30000, "property_type": "2BHK", "top_n": 5}' \
  | python3 -m json.tool

# Test Gwalior
curl -X POST "http://localhost:8000/api/v1/recommendations/neighborhoods" \
  -H "Content-Type: application/json" \
  -d '{"city": "Gwalior", "number_of_people": 2, "max_travel_distance_km": 5, "budget": 25000, "property_type": "2BHK", "top_n": 5}' \
  | python3 -m json.tool
```

#### Check Available Cities:
```bash
curl "http://localhost:8000/api/v1/geospatial/localities" | python3 -m json.tool | grep -A 1 '"city"'
```

### 3. **Database Verification**

```bash
# Check all cities and localities
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT city, COUNT(*) as localities FROM localities GROUP BY city ORDER BY city;"

# Check neighborhood data with food/grocery info
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT city, locality_id, avg_grocery_cost_monthly, restaurants_count, \
   avg_restaurant_rating, grocery_stores_count \
   FROM neighborhood_data \
   WHERE city = 'Indore' \
   LIMIT 5;"
```

### 4. **Run Automated Tests**

```bash
# Run comprehensive test suite
./test_all.sh
```

### 5. **Test ML Model**

```bash
# Test the trained model
docker-compose exec ml-worker python test_model.py
```

## ✅ What to Verify

### Frontend:
- [ ] City dropdown shows all MP cities
- [ ] Recommendations appear for each city
- [ ] Food & Beverages section displays:
  - Restaurant count
  - Restaurant ratings
  - Grocery stores count
- [ ] Grocery cost is shown (not "N/A")
- [ ] All amenities are displayed

### Backend:
- [ ] API returns recommendations for all cities
- [ ] Response includes `restaurants_count`, `grocery_stores_count`
- [ ] Response includes `avg_restaurant_rating`
- [ ] `grocery_cost` is populated (not null)

### Database:
- [ ] All 7 MP cities have localities
- [ ] Neighborhood data exists for all cities
- [ ] Food/grocery data is being collected

## 🔧 Troubleshooting

### If recommendations don't show:
1. Check if neighborhood data exists:
   ```bash
   docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
     "SELECT city, COUNT(*) FROM neighborhood_data GROUP BY city;"
   ```

2. Refresh data for a city:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/recommendations/refresh/Indore"
   ```

### If food/grocery data is missing:
1. Check ML worker logs:
   ```bash
   docker-compose logs ml-worker --tail=50
   ```

2. Verify APIs are working:
   ```bash
   docker-compose logs backend --tail=50 | grep -i "error\|api"
   ```


# Data Sources for Rent, Groceries, and Transport

This document explains where the application fetches data for **Rent**, **Groceries**, and **Transport** costs.

## 📍 Data Flow Overview

The data is fetched from **two main sources**:
1. **Public APIs** (used during ML model training and neighborhood data aggregation)
2. **Database** (stored data used for predictions and recommendations)

---

## 🏠 **RENT DATA**

### During Training (ML Worker)
**Location:** `ml_worker/train_cost_predictor.py`

**Source:** 
- **Primary:** Overpass API (OpenStreetMap)
  - URL: `https://overpass-api.de/api/interpreter`
  - Queries residential buildings within 1km radius
  - Estimates rent based on building density and city averages

**Method:**
```python
def fetch_rent_from_public_apis(locality, city, latitude, longitude):
    # 1. Query Overpass API for residential buildings
    # 2. Count buildings in area
    # 3. Apply city-based base rents:
    #    - Bhopal: 1BHK=₹8K, 2BHK=₹12K, 3BHK=₹18K
    #    - Indore: 1BHK=₹10K, 2BHK=₹15K, 3BHK=₹22K
    #    - Gwalior: 1BHK=₹7K, 2BHK=₹11K, 3BHK=₹16K
    #    - Jabalpur: 1BHK=₹7.5K, 2BHK=₹11.5K, 3BHK=₹17K
    #    - Ujjain: 1BHK=₹6K, 2BHK=₹9K, 3BHK=₹13K
    # 4. Adjust based on building density
```

**Fallback:** City average rents if API fails

### During Runtime (Backend)
**Location:** `backend/app/services/rent_service.py`

**Source:** 
- **Database** (`rent_listings` table)
- Calculates average rent from stored listings

**Method:**
```python
def get_avg_rent_by_locality(locality_id, property_type):
    # Queries database for average rent
    # Returns average of all listings for that locality
```

**Scraping Services (Placeholder):**
- NoBroker scraping (not fully implemented)
- OLX scraping (not fully implemented)

---

## 🛒 **GROCERY DATA**

### During Training (ML Worker)
**Location:** `ml_worker/train_cost_predictor.py`

**Source:**
- **Delivery Service APIs** (Blinkit, Zomato, Swiggy)
- Uses delivery availability to infer grocery store presence
- Estimates cost based on city averages and delivery options

**Method:**
```python
def fetch_grocery_cost_from_public_apis(latitude, longitude, city):
    # 1. Check delivery service availability (Blinkit, Zomato, Swiggy)
    # 2. Base costs by city:
    #    - Bhopal: ₹4,500/month
    #    - Indore: ₹5,000/month
    #    - Gwalior: ₹4,200/month
    #    - Jabalpur: ₹4,300/month
    #    - Ujjain: ₹4,000/month
    # 3. Adjust based on delivery service count
    #    (More delivery options = more competition = adjusted pricing)
```

**Fallback:** City average (₹4,500/month)

### During Runtime (Backend)
**Location:** `backend/app/services/grocery_service.py`

**Source:**
- **Database** (`grocery_stores` and `grocery_items` tables)
- Calculates cost from stored store items

**Method:**
```python
def calculate_monthly_grocery_cost(locality_id, items):
    # 1. Get all grocery stores for locality
    # 2. Find items in stores
    # 3. Calculate total cost based on item prices
```

**API Services (Placeholder):**
- BigBasket API (not fully implemented - requires API key)
- Blinkit API (not fully implemented - requires API key)

---

## 🚌 **TRANSPORT DATA**

### During Training (ML Worker)
**Location:** `ml_worker/train_cost_predictor.py`

**Source:**
- **Amenities Service** (checks bus stops, metro stations via Overpass API)
- Estimates cost based on connectivity and city averages

**Method:**
```python
def fetch_transport_cost_from_public_apis(latitude, longitude, city):
    # 1. Get nearby amenities (bus stops, metro stations)
    # 2. Base costs by city:
    #    - Bhopal: ₹2,500/month
    #    - Indore: ₹3,000/month
    #    - Gwalior: ₹2,200/month
    #    - Jabalpur: ₹2,400/month
    #    - Ujjain: ₹2,000/month
    # 3. Adjust based on connectivity
    #    (More bus stops/metro = better connectivity = lower costs)
```

**Fallback:** City average (₹2,500/month)

### During Runtime (Backend)
**Location:** `backend/app/services/transport_service.py`

**Source:**
- **Database** (`transport_routes` and `transport_fares` tables)
- Calculates cost from stored routes and fares

**Method:**
```python
def calculate_monthly_transport_cost(source_id, dest_id, trips_per_month):
    # 1. Find route between localities
    # 2. Get current fare
    # 3. Calculate: fare * trips_per_month
```

**API Services (Placeholder):**
- BCLL (Bhopal City Link Limited) API (not fully implemented)

---

## 📊 **How Data is Used**

### 1. **ML Model Training** (`ml_worker/train_cost_predictor.py`)
- Fetches data from public APIs for all MP cities
- Creates training dataset with real API data
- Trains XGBoost model on this data

### 2. **Neighborhood Data Aggregation** (`backend/app/services/neighborhood_service.py`)
- Aggregates data from public APIs
- Stores in `neighborhood_data` table
- Used for recommendations

### 3. **Locality Stats** (`backend/app/services/geospatial_service.py`)
- Calculates averages from database
- Stores in `locality_stats` table
- Used for cost predictions

### 4. **Cost Predictions** (`backend/app/services/ml_service.py`)
- Uses `locality_stats` from database
- If stats missing, creates them automatically
- Returns predictions with breakdown

---

## 🔄 **Data Update Flow**

```
Public APIs (Training)
    ↓
ML Model Training
    ↓
Neighborhood Data Aggregation
    ↓
Database (locality_stats, neighborhood_data)
    ↓
Cost Predictions & Recommendations
```

---

## ⚠️ **Current Limitations**

1. **Rent Data:**
   - Uses city averages with density adjustments
   - NoBroker/OLX scraping not fully implemented
   - Relies on Overpass API for building density

2. **Grocery Data:**
   - Uses city averages with delivery service adjustments
   - BigBasket/Blinkit APIs require API keys (not configured)
   - Falls back to estimates

3. **Transport Data:**
   - Uses city averages with connectivity adjustments
   - BCLL API not fully implemented
   - Relies on amenities data for connectivity

---

## 🚀 **Future Improvements**

1. **Rent:**
   - Integrate NoBroker/OLX APIs
   - Add MagicBricks/99acres scraping
   - Use actual rental listings

2. **Grocery:**
   - Integrate BigBasket/Blinkit APIs
   - Fetch actual product prices
   - Calculate real basket costs

3. **Transport:**
   - Integrate BCLL/other transport APIs
   - Fetch real-time fares
   - Add route optimization

---

## 📝 **Summary**

| Data Type | Training Source | Runtime Source | Status |
|-----------|----------------|----------------|--------|
| **Rent** | Overpass API + City Averages | Database (rent_listings) | ⚠️ Partial |
| **Grocery** | Delivery APIs + City Averages | Database (grocery_stores) | ⚠️ Partial |
| **Transport** | Amenities API + City Averages | Database (transport_routes) | ⚠️ Partial |

**Note:** Currently using **city-based estimates** with adjustments from public APIs. Full API integrations require API keys and additional implementation.


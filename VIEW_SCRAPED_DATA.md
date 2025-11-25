# How to View Scraped Data in Frontend

## 🎯 Quick Access

1. **Open the application:**
   ```
   http://localhost
   ```

2. **Navigate to "Scraped Data" page:**
   - Click on "Scraped Data" in the navigation menu
   - Or go directly to: `http://localhost/scraped-data`

## 📊 What You Can See

### Rent Listings Tab
- **All rent listings** scraped from NoBroker and OLX
- **Filter by locality** - Select any Bhopal locality
- **Details shown:**
  - Property type (1BHK, 2BHK, 3BHK)
  - Rent amount
  - Area (if available)
  - Address
  - Source (nobroker, olx, etc.)

### Grocery Items Tab
- **All grocery products** scraped from BigBasket
- **Filter by locality** - Select any Bhopal locality
- **Details shown:**
  - Product name
  - Price
  - Category
  - Unit (kg, L, piece, etc.)
  - Brand (if available)

## 🔍 Other Ways to View Data

### 1. Locality Comparison Page
- Go to "Locality Comparison"
- Select Bhopal localities
- See average rent and grocery costs

### 2. Find Neighborhood Page
- Go to "Find Neighborhood"
- Select city: "Bhopal"
- Recommendations include scraped rent and grocery data

### 3. Cost Prediction Page
- Go to "Cost Prediction"
- Select a Bhopal locality
- Predictions use scraped data

## 📈 Current Data Summary

**Rent Listings:**
- Total: 58 listings
- Localities: 5 (Arera Colony, MP Nagar, New Market, Hoshangabad Road, Shahpura)
- Property Types: 1BHK, 2BHK, 3BHK

**Grocery Items:**
- Total: 40 products
- Stores: 5 BigBasket stores
- Products: Rice, Wheat, Milk, Eggs, Onion, Potato, Tomato, Cooking Oil

## 🔄 Refresh Data

To get latest scraped data:
```bash
curl -X POST "http://localhost:8000/api/v1/scraping/bhopal/all"
```

Then refresh the frontend page to see updated data.


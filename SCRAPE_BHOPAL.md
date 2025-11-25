# Web Scraping for Bhopal

This document explains how to use the web scraping functionality for Bhopal data.

## 🎯 Overview

The scraping system fetches real data from:
- **Rent:** NoBroker, OLX
- **Grocery:** BigBasket
- **Transport:** BCLL (Bhopal City Link Limited)

## 🚀 Usage

### Option 1: Using API Endpoints

#### Scrape All Bhopal Data
```bash
curl -X POST "http://localhost:8000/api/v1/scraping/bhopal/all"
```

#### Scrape Only Rent Data
```bash
curl -X POST "http://localhost:8000/api/v1/scraping/bhopal/rent"
```

#### Scrape Only Grocery Data
```bash
curl -X POST "http://localhost:8000/api/v1/scraping/bhopal/grocery"
```

### Option 2: Direct Script Execution

```bash
docker-compose exec backend python scrape_bhopal.py
```

## 📊 What Gets Scraped

### Rent Data
- **Sources:** NoBroker, OLX
- **Data:** Rent amounts, property types (1BHK, 2BHK, 3BHK)
- **Stored in:** `rent_listings` table
- **Localities:** All Bhopal localities

### Grocery Data
- **Sources:** BigBasket
- **Data:** Product names, prices, categories
- **Stored in:** `grocery_stores` and `grocery_items` tables
- **Items:** Rice, Wheat, Milk, Eggs, Onion, Potato, Tomato, Oil

### Transport Data
- **Sources:** BCLL (Bhopal City Link Limited)
- **Data:** Bus routes, fares
- **Stored in:** `transport_routes` and `transport_fares` tables

## ⚙️ Configuration

The scraper includes:
- **Rate Limiting:** 2-3 seconds between requests
- **Timeout:** 20 seconds per request
- **Error Handling:** Continues on errors, logs warnings
- **Duplicate Prevention:** Checks database before saving

## 📝 Notes

1. **Anti-Scraping Measures:** Some websites may block scrapers. The script includes:
   - Proper User-Agent headers
   - Rate limiting
   - Error handling

2. **Data Quality:** 
   - Rent data is validated (₹5,000 - ₹50,000 range)
   - Duplicates are prevented
   - Source is tracked for each listing

3. **Performance:**
   - Scraping all Bhopal data takes ~5-10 minutes
   - Individual locality takes ~30-60 seconds

## 🔍 Verifying Scraped Data

```bash
# Check rent listings
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT COUNT(*), source FROM rent_listings WHERE source IN ('nobroker', 'olx') GROUP BY source;"

# Check grocery products
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT COUNT(*) FROM grocery_items;"

# Check transport routes
docker-compose exec postgres psql -U postgres -d mpcostpulse -c \
  "SELECT COUNT(*) FROM transport_routes;"
```

## 🛠️ Troubleshooting

### Timeout Errors
- Increase timeout in script (currently 20 seconds)
- Check network connectivity
- Some sites may be blocking requests

### No Data Scraped
- Check if websites have changed their HTML structure
- Verify locality names match website URLs
- Check logs for specific errors

### Rate Limiting
- Increase sleep times between requests
- Use proxy rotation (not implemented)
- Consider using official APIs if available

## 📈 Future Improvements

1. **Add More Sources:**
   - MagicBricks for rent
   - 99acres for rent
   - Blinkit for groceries
   - Swiggy Instamart for groceries

2. **Better Parsing:**
   - Use Selenium for JavaScript-heavy sites
   - Implement machine learning for data extraction
   - Add image recognition for property photos

3. **Scheduling:**
   - Add cron job for daily scraping
   - Implement incremental updates
   - Track data freshness


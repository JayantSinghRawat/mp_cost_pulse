#!/usr/bin/env python3
"""
Seed script to add localities for all MP cities
This creates localities and initial neighborhood data for cities other than Bhopal
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, init_db
from app.models.geospatial import Locality, LocalityStats
from app.models.neighborhood import NeighborhoodData
from app.services.neighborhood_service import NeighborhoodService
import requests
import time

# MP Cities and their localities with coordinates
MP_CITIES_DATA = {
    "Indore": {
        "localities": [
            {"name": "Vijay Nagar", "lat": 22.7186, "lon": 75.8577},
            {"name": "Saket Nagar", "lat": 22.7234, "lon": 75.8601},
            {"name": "Scheme 54", "lat": 22.7156, "lon": 75.8623},
            {"name": "Palasia", "lat": 22.7200, "lon": 75.8580},
            {"name": "MG Road", "lat": 22.7175, "lon": 75.8590},
        ]
    },
    "Gwalior": {
        "localities": [
            {"name": "City Center", "lat": 26.2183, "lon": 78.1828},
            {"name": "Thatipur", "lat": 26.2200, "lon": 78.1800},
            {"name": "Lashkar", "lat": 26.2150, "lon": 78.1850},
            {"name": "Morar", "lat": 26.2250, "lon": 78.1900},
        ]
    },
    "Jabalpur": {
        "localities": [
            {"name": "Civil Lines", "lat": 23.1815, "lon": 79.9864},
            {"name": "Wright Town", "lat": 23.1850, "lon": 79.9900},
            {"name": "Napier Town", "lat": 23.1800, "lon": 79.9850},
            {"name": "Gwarighat", "lat": 23.1750, "lon": 79.9800},
        ]
    },
    "Ujjain": {
        "localities": [
            {"name": "Freeganj", "lat": 23.1765, "lon": 75.7885},
            {"name": "Dewas Gate", "lat": 23.1800, "lon": 75.7900},
            {"name": "Nanakheda", "lat": 23.1750, "lon": 75.7850},
        ]
    },
    "Sagar": {
        "localities": [
            {"name": "Civil Lines", "lat": 23.8388, "lon": 78.7381},
            {"name": "Gulab Nagar", "lat": 23.8400, "lon": 78.7400},
        ]
    },
    "Ratlam": {
        "localities": [
            {"name": "Station Road", "lat": 23.3341, "lon": 75.0376},
            {"name": "Gandhi Nagar", "lat": 23.3360, "lon": 75.0400},
        ]
    },
}

# Base rent estimates for MP cities (per 2BHK)
CITY_RENT_ESTIMATES = {
    "Indore": {"2BHK": 15000, "1BHK": 10000, "3BHK": 22000},
    "Gwalior": {"2BHK": 11000, "1BHK": 7000, "3BHK": 16000},
    "Jabalpur": {"2BHK": 11500, "1BHK": 7500, "3BHK": 17000},
    "Ujjain": {"2BHK": 9000, "1BHK": 6000, "3BHK": 13000},
    "Sagar": {"2BHK": 8000, "1BHK": 5500, "3BHK": 12000},
    "Ratlam": {"2BHK": 8500, "1BHK": 6000, "3BHK": 12500},
}

# Base grocery and transport costs
CITY_COSTS = {
    "Indore": {"grocery": 5000, "transport": 3000},
    "Gwalior": {"grocery": 4200, "transport": 2200},
    "Jabalpur": {"grocery": 4300, "transport": 2400},
    "Ujjain": {"grocery": 4000, "transport": 2000},
    "Sagar": {"grocery": 3800, "transport": 1800},
    "Ratlam": {"grocery": 3900, "transport": 1900},
}

def get_coordinates_from_nominatim(locality_name: str, city: str):
    """Get coordinates from Nominatim if not provided"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{locality_name}, {city}, Madhya Pradesh, India",
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "MPCostPulse-Seed/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        time.sleep(1)  # Rate limiting
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0].get("lat", 0)), float(data[0].get("lon", 0))
    except Exception as e:
        print(f"Error fetching coordinates for {locality_name}, {city}: {e}")
    return None, None

def seed_localities():
    """Seed localities for all MP cities"""
    db = SessionLocal()
    
    try:
        init_db()  # Ensure tables exist
        
        total_created = 0
        
        for city, city_data in MP_CITIES_DATA.items():
            print(f"\nProcessing {city}...")
            
            for locality_info in city_data["localities"]:
                locality_name = locality_info["name"]
                
                # Check if locality already exists (check by name AND city to avoid duplicates)
                existing = db.query(Locality).filter(
                    Locality.name == locality_name,
                    Locality.city == city
                ).first()
                
                if existing:
                    print(f"  ✓ {locality_name}, {city} already exists")
                    continue
                
                # Also check if same name exists in different city (to avoid unique constraint violation)
                name_exists = db.query(Locality).filter(
                    Locality.name == locality_name
                ).first()
                
                if name_exists and name_exists.city != city:
                    # Use a unique name for this city
                    locality_name = f"{locality_name}, {city}"
                    print(f"  ⚠ Renaming to {locality_name} to avoid duplicate")
                
                # Get coordinates
                lat = locality_info.get("lat")
                lon = locality_info.get("lon")
                
                if not lat or not lon:
                    lat, lon = get_coordinates_from_nominatim(locality_name, city)
                    if not lat or not lon:
                        print(f"  ✗ Could not get coordinates for {locality_name}")
                        continue
                
                # Create locality
                locality = Locality(
                    name=locality_name,
                    city=city,
                    state="Madhya Pradesh",
                    latitude=lat,
                    longitude=lon
                )
                db.add(locality)
                db.flush()  # Get the ID
                
                # Create locality stats with estimated values
                rent_estimates = CITY_RENT_ESTIMATES.get(city, {"2BHK": 10000, "1BHK": 7000, "3BHK": 15000})
                costs = CITY_COSTS.get(city, {"grocery": 4500, "transport": 2500})
                
                stats = LocalityStats(
                    locality_id=locality.id,
                    avg_rent_1bhk=rent_estimates.get("1BHK"),
                    avg_rent_2bhk=rent_estimates.get("2BHK"),
                    avg_rent_3bhk=rent_estimates.get("3BHK"),
                    avg_grocery_cost_monthly=costs.get("grocery"),
                    avg_transport_cost_monthly=costs.get("transport"),
                    cost_burden_index=((rent_estimates.get("2BHK") + costs.get("grocery") + costs.get("transport")) / 50000) * 100
                )
                db.add(stats)
                
                # Create initial neighborhood data
                neighborhood = NeighborhoodData(
                    locality_id=locality.id,
                    city=city,
                    avg_rent_1bhk=rent_estimates.get("1BHK"),
                    avg_rent_2bhk=rent_estimates.get("2BHK"),
                    avg_rent_3bhk=rent_estimates.get("3BHK"),
                    avg_grocery_cost_monthly=costs.get("grocery"),
                    # Set default values for other fields
                    aqi_value=50,  # Moderate AQI
                    aqi_category="Moderate",
                    amenities_score=5.0,
                    connectivity_score=5.0,
                )
                db.add(neighborhood)
                
                print(f"  ✓ Created {locality_name} (lat: {lat}, lon: {lon})")
                total_created += 1
        
        db.commit()
        print(f"\n✅ Successfully created {total_created} new localities")
        
        # Now aggregate neighborhood data for all new localities
        print("\nAggregating neighborhood data...")
        for city, city_data in MP_CITIES_DATA.items():
            for locality_info in city_data["localities"]:
                locality = db.query(Locality).filter(
                    Locality.name == locality_info["name"],
                    Locality.city == city
                ).first()
                
                if locality:
                    try:
                        NeighborhoodService.aggregate_neighborhood_data(
                            db=db,
                            locality_id=locality.id,
                            city=city
                        )
                        print(f"  ✓ Aggregated data for {locality_info['name']}, {city}")
                    except Exception as e:
                        print(f"  ⚠ Could not aggregate data for {locality_info['name']}, {city}: {e}")
        
        db.commit()
        print("\n✅ Seeding completed!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_localities()


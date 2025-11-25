#!/usr/bin/env python3
"""
Seed Bhopal localities for scraping
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, init_db
from app.models.geospatial import Locality, LocalityStats
import requests
import time

# Bhopal localities with approximate coordinates
BHOPAL_LOCALITIES = [
    {"name": "Arera Colony", "lat": 23.2295, "lon": 77.4126},
    {"name": "MP Nagar", "lat": 23.2350, "lon": 77.4080},
    {"name": "New Market", "lat": 23.2569, "lon": 77.4010},
    {"name": "Hoshangabad Road", "lat": 23.2400, "lon": 77.4200},
    {"name": "Shahpura", "lat": 23.2500, "lon": 77.4100},
    {"name": "Bairagarh", "lat": 23.2200, "lon": 77.4000},
    {"name": "Kolar", "lat": 23.2100, "lon": 77.4300},
    {"name": "Awadhpuri", "lat": 23.2300, "lon": 77.4150},
    {"name": "Saket Nagar", "lat": 23.2450, "lon": 77.4050},
]

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

def seed_bhopal_localities():
    """Seed Bhopal localities"""
    db = SessionLocal()
    
    try:
        init_db()  # Ensure tables exist
        
        total_created = 0
        
        for locality_info in BHOPAL_LOCALITIES:
            locality_name = locality_info["name"]
            
            # Check if locality already exists
            existing = db.query(Locality).filter(
                Locality.name == locality_name,
                Locality.city == "Bhopal"
            ).first()
            
            if existing:
                print(f"  ✓ {locality_name}, Bhopal already exists")
                continue
            
            # Get coordinates
            lat = locality_info.get("lat")
            lon = locality_info.get("lon")
            
            if not lat or not lon:
                lat, lon = get_coordinates_from_nominatim(locality_name, "Bhopal")
                if not lat or not lon:
                    print(f"  ✗ Could not get coordinates for {locality_name}")
                    continue
            
            # Create locality
            locality = Locality(
                name=locality_name,
                city="Bhopal",
                state="Madhya Pradesh",
                latitude=lat,
                longitude=lon
            )
            db.add(locality)
            db.flush()  # Get the ID
            
            # Create locality stats with default values
            stats = LocalityStats(
                locality_id=locality.id,
                avg_rent_1bhk=8000,
                avg_rent_2bhk=12000,
                avg_rent_3bhk=18000,
                avg_grocery_cost_monthly=4500,
                avg_transport_cost_monthly=2500,
                cost_burden_index=((12000 + 4500 + 2500) / 50000) * 100
            )
            db.add(stats)
            
            print(f"  ✓ Created {locality_name} (lat: {lat}, lon: {lon})")
            total_created += 1
        
        db.commit()
        print(f"\n✅ Successfully created {total_created} new Bhopal localities")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_bhopal_localities()


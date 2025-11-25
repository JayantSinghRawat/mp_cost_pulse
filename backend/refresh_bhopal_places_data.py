#!/usr/bin/env python3
"""
Refresh Bhopal neighborhood data using Google Places API
Fetches real data for restaurants, grocery stores, hospitals, schools, parks, malls
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.geospatial import Locality
from app.services.neighborhood_service import NeighborhoodService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_bhopal_places_data():
    """Refresh all Bhopal neighborhoods with Google Places API data"""
    db = SessionLocal()
    
    try:
        # Get all Bhopal localities
        localities = db.query(Locality).filter(Locality.city == 'Bhopal').all()
        logger.info(f"Found {len(localities)} Bhopal localities")
        logger.info("Using Google Places API to fetch:")
        logger.info("  - Restaurants")
        logger.info("  - Grocery Stores")
        logger.info("  - Hospitals")
        logger.info("  - Schools")
        logger.info("  - Parks")
        logger.info("  - Malls")
        logger.info("")
        
        updated = 0
        for locality in localities:
            try:
                logger.info(f"Refreshing {locality.name}...")
                NeighborhoodService.aggregate_neighborhood_data(db, locality.id, 'Bhopal')
                updated += 1
                logger.info(f"  ✓ Updated {locality.name}")
            except Exception as e:
                logger.error(f"  ✗ Error updating {locality.name}: {e}")
        
        db.commit()
        logger.info(f"\n✅ Updated {updated} neighborhoods with Google Places data")
        
        # Show summary
        from app.models.neighborhood import NeighborhoodData
        from sqlalchemy import func
        
        summary = db.query(
            func.avg(NeighborhoodData.restaurants_count).label('avg_restaurants'),
            func.avg(NeighborhoodData.grocery_stores_count).label('avg_grocery_stores'),
            func.avg(NeighborhoodData.hospitals_count).label('avg_hospitals'),
            func.avg(NeighborhoodData.schools_count).label('avg_schools'),
            func.avg(NeighborhoodData.parks_count).label('avg_parks'),
            func.avg(NeighborhoodData.shopping_malls_count).label('avg_malls'),
            func.count(NeighborhoodData.id).label('count')
        ).filter(
            NeighborhoodData.city == 'Bhopal'
        ).first()
        
        logger.info(f"\nSummary (Bhopal):")
        logger.info(f"  Average Restaurants: {summary.avg_restaurants:.1f}")
        logger.info(f"  Average Grocery Stores: {summary.avg_grocery_stores:.1f}")
        logger.info(f"  Average Hospitals: {summary.avg_hospitals:.1f}")
        logger.info(f"  Average Schools: {summary.avg_schools:.1f}")
        logger.info(f"  Average Parks: {summary.avg_parks:.1f}")
        logger.info(f"  Average Malls: {summary.avg_malls:.1f}")
        logger.info(f"  Neighborhoods updated: {summary.count}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    refresh_bhopal_places_data()


#!/usr/bin/env python3
"""
Refresh all neighborhood data for MP cities using public APIs
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

MP_CITIES = ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Ratlam"]

def refresh_all_cities():
    """Refresh neighborhood data for all MP cities"""
    db = SessionLocal()
    
    try:
        for city in MP_CITIES:
            logger.info(f"\n{'='*60}")
            logger.info(f"Refreshing {city}...")
            logger.info(f"{'='*60}")
            
            localities = db.query(Locality).filter(Locality.city == city).all()
            logger.info(f"Found {len(localities)} localities in {city}")
            
            for locality in localities:
                try:
                    logger.info(f"  Refreshing {locality.name}...")
                    NeighborhoodService.aggregate_neighborhood_data(
                        db=db,
                        locality_id=locality.id,
                        city=city
                    )
                    logger.info(f"  ✓ {locality.name} refreshed")
                except Exception as e:
                    logger.error(f"  ✗ Error refreshing {locality.name}: {e}")
            
            db.commit()
            logger.info(f"✅ {city} completed")
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ All cities refreshed!")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    refresh_all_cities()


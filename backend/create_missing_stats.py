#!/usr/bin/env python3
"""
Create locality stats for all localities that don't have them
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.geospatial import Locality, LocalityStats
from app.services.geospatial_service import GeospatialService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_missing_stats():
    """Create stats for all localities that don't have them"""
    db = SessionLocal()
    
    try:
        # Get all localities
        localities = db.query(Locality).all()
        logger.info(f"Found {len(localities)} localities")
        
        # Get localities without stats
        localities_with_stats = db.query(LocalityStats.locality_id).distinct().all()
        locality_ids_with_stats = {row[0] for row in localities_with_stats}
        
        missing_count = 0
        for locality in localities:
            if locality.id not in locality_ids_with_stats:
                try:
                    logger.info(f"Creating stats for {locality.name} (ID: {locality.id})")
                    GeospatialService.update_locality_stats(db, locality.id)
                    missing_count += 1
                except Exception as e:
                    logger.error(f"Error creating stats for {locality.name}: {e}")
        
        db.commit()
        logger.info(f"✅ Created stats for {missing_count} localities")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_missing_stats()


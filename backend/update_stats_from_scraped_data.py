#!/usr/bin/env python3
"""
Update locality stats from scraped data for all Bhopal localities
This ensures recommendations and predictions use real scraped data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.geospatial import Locality
from app.services.geospatial_service import GeospatialService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_all_bhopal_stats():
    """Update locality stats for all Bhopal localities using scraped data"""
    db = SessionLocal()
    
    try:
        # Get all Bhopal localities
        localities = db.query(Locality).filter(Locality.city == 'Bhopal').all()
        logger.info(f"Found {len(localities)} Bhopal localities")
        
        updated = 0
        for locality in localities:
            try:
                logger.info(f"Updating stats for {locality.name}...")
                GeospatialService.update_locality_stats(db, locality.id)
                updated += 1
                logger.info(f"  ✓ Updated {locality.name}")
            except Exception as e:
                logger.error(f"  ✗ Error updating {locality.name}: {e}")
        
        db.commit()
        logger.info(f"\n✅ Updated stats for {updated} localities")
        
        # Show summary
        from app.models.geospatial import LocalityStats
        from sqlalchemy import func
        
        stats_summary = db.query(
            func.avg(LocalityStats.avg_rent_2bhk).label('avg_rent'),
            func.avg(LocalityStats.avg_grocery_cost_monthly).label('avg_grocery'),
            func.count(LocalityStats.locality_id).label('count')
        ).filter(
            LocalityStats.locality_id.in_([l.id for l in localities])
        ).first()
        
        logger.info(f"\nSummary:")
        logger.info(f"  Average Rent (2BHK): ₹{stats_summary.avg_rent:.0f}")
        logger.info(f"  Average Grocery Cost: ₹{stats_summary.avg_grocery:.0f}")
        logger.info(f"  Localities with stats: {stats_summary.count}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_all_bhopal_stats()


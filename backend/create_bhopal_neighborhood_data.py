#!/usr/bin/env python3
"""
Create neighborhood_data entries for Bhopal localities from scraped data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.geospatial import Locality, LocalityStats
from app.models.neighborhood import NeighborhoodData
from app.models.rent import RentListing
from app.models.grocery import GroceryStore, GroceryItem
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_neighborhood_data():
    """Create neighborhood_data entries for all Bhopal localities"""
    db = SessionLocal()
    
    try:
        # Get all Bhopal localities
        localities = db.query(Locality).filter(Locality.city == 'Bhopal').all()
        logger.info(f"Found {len(localities)} Bhopal localities")
        
        created = 0
        updated = 0
        
        for locality in localities:
            # Check if neighborhood_data already exists
            neighborhood = db.query(NeighborhoodData).filter(
                NeighborhoodData.locality_id == locality.id
            ).first()
            
            if neighborhood:
                logger.info(f"  Neighborhood data already exists for {locality.name}")
                updated += 1
                continue
            
            # Get locality stats
            stats = db.query(LocalityStats).filter(
                LocalityStats.locality_id == locality.id
            ).first()
            
            # Calculate average rent from scraped listings
            avg_rent_1bhk = db.query(func.avg(RentListing.rent_amount)).filter(
                RentListing.locality_id == locality.id,
                RentListing.property_type == '1BHK'
            ).scalar()
            
            avg_rent_2bhk = db.query(func.avg(RentListing.rent_amount)).filter(
                RentListing.locality_id == locality.id,
                RentListing.property_type == '2BHK'
            ).scalar()
            
            avg_rent_3bhk = db.query(func.avg(RentListing.rent_amount)).filter(
                RentListing.locality_id == locality.id,
                RentListing.property_type == '3BHK'
            ).scalar()
            
            # Use stats if rent not found in listings
            if not avg_rent_1bhk and stats:
                avg_rent_1bhk = stats.avg_rent_1bhk
            if not avg_rent_2bhk and stats:
                avg_rent_2bhk = stats.avg_rent_2bhk
            if not avg_rent_3bhk and stats:
                avg_rent_3bhk = stats.avg_rent_3bhk
            
            # Get rent listings count
            rent_count = db.query(RentListing).filter(
                RentListing.locality_id == locality.id
            ).count()
            
            # Get grocery stores count
            grocery_stores_count = db.query(GroceryStore).filter(
                GroceryStore.locality_id == locality.id
            ).count()
            
            # Get average grocery cost from stats or calculate from items
            avg_grocery_cost = None
            if stats and stats.avg_grocery_cost_monthly:
                avg_grocery_cost = stats.avg_grocery_cost_monthly
            else:
                # Calculate from grocery items
                grocery_stores = db.query(GroceryStore).filter(
                    GroceryStore.locality_id == locality.id
                ).all()
                if grocery_stores:
                    total_cost = 0
                    item_count = 0
                    for store in grocery_stores:
                        items = db.query(GroceryItem).filter(
                            GroceryItem.store_id == store.id
                        ).all()
                        for item in items:
                            total_cost += item.price
                            item_count += 1
                    if item_count > 0:
                        # Estimate monthly cost (multiply by typical monthly quantities)
                        avg_grocery_cost = (total_cost / item_count) * 30
            
            # Create neighborhood data
            neighborhood = NeighborhoodData(
                locality_id=locality.id,
                city='Bhopal',
                avg_rent_1bhk=avg_rent_1bhk or 8000,
                avg_rent_2bhk=avg_rent_2bhk or 12000,
                avg_rent_3bhk=avg_rent_3bhk or 18000,
                rent_listings_count=rent_count,
                avg_grocery_cost_monthly=avg_grocery_cost or 4500,
                grocery_stores_count=grocery_stores_count,
                # Set default values
                aqi_value=50,
                aqi_category='Moderate',
                amenities_score=5.0,
                connectivity_score=5.0,
                safety_score=7.0,
                blinkit_available=False,
                zomato_available=False,
                swiggy_available=False,
                restaurants_count=0,
                hospitals_count=0,
                schools_count=0,
                parks_count=0,
                shopping_malls_count=0
            )
            
            db.add(neighborhood)
            logger.info(f"  ✓ Created neighborhood data for {locality.name}")
            created += 1
        
        db.commit()
        logger.info(f"\n✅ Created {created} neighborhood data entries")
        logger.info(f"✅ Updated {updated} existing entries")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_neighborhood_data()


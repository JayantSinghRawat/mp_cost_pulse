from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from app.models.rent import RentListing
from app.models.geospatial import Locality
from app.schemas.rent import RentListingCreate
import requests
from bs4 import BeautifulSoup
import time
from app.core.config import settings

class RentService:
    @staticmethod
    def get_listings(
        db: Session,
        locality_id: Optional[int] = None,
        property_type: Optional[str] = None,
        min_rent: Optional[float] = None,
        max_rent: Optional[float] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[RentListing]:
        """Get rent listings with filters"""
        query = db.query(RentListing)
        
        if locality_id:
            query = query.filter(RentListing.locality_id == locality_id)
        if property_type:
            query = query.filter(RentListing.property_type == property_type)
        if min_rent:
            query = query.filter(RentListing.rent_amount >= min_rent)
        if max_rent:
            query = query.filter(RentListing.rent_amount <= max_rent)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_avg_rent_by_locality(
        db: Session,
        locality_id: int,
        property_type: Optional[str] = None
    ) -> Optional[float]:
        """Calculate average rent for a locality"""
        query = db.query(func.avg(RentListing.rent_amount)).filter(
            RentListing.locality_id == locality_id
        )
        if property_type:
            query = query.filter(RentListing.property_type == property_type)
        
        result = query.scalar()
        return float(result) if result else None
    
    @staticmethod
    def scrape_nobroker(locality: str, city: str = "Bhopal") -> List[dict]:
        """Scrape NoBroker listings"""
        listings = []
        try:
            # NoBroker API or scraping logic
            # This is a placeholder - actual implementation would use their API or scrape
            url = f"https://www.nobroker.in/property/rent/{city}/{locality}"
            headers = {"User-Agent": settings.USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse listings from HTML
                # This is simplified - actual scraping would be more complex
                time.sleep(settings.SCRAPY_DELAY)
        except Exception as e:
            print(f"Error scraping NoBroker: {e}")
        
        return listings
    
    @staticmethod
    def scrape_olx(locality: str, city: str = "Bhopal") -> List[dict]:
        """Scrape OLX listings"""
        listings = []
        try:
            # OLX scraping logic
            url = f"https://www.olx.in/{city}/q-rent-{locality}"
            headers = {"User-Agent": settings.USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse listings from HTML
                time.sleep(settings.SCRAPY_DELAY)
        except Exception as e:
            print(f"Error scraping OLX: {e}")
        
        return listings
    
    @staticmethod
    def create_listing(db: Session, listing: RentListingCreate) -> RentListing:
        """Create a new rent listing"""
        db_listing = RentListing(**listing.dict())
        db.add(db_listing)
        db.commit()
        db.refresh(db_listing)
        return db_listing


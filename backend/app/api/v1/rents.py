from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.rent_service import RentService
from app.schemas.rent import RentListingResponse, RentListingCreate

router = APIRouter(prefix="/rents", tags=["rents"])

@router.get("/", response_model=List[RentListingResponse])
def get_rent_listings(
    locality_id: Optional[int] = Query(None),
    property_type: Optional[str] = Query(None),
    min_rent: Optional[float] = Query(None),
    max_rent: Optional[float] = Query(None),
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get rent listings with optional filters"""
    listings = RentService.get_listings(
        db=db,
        locality_id=locality_id,
        property_type=property_type,
        min_rent=min_rent,
        max_rent=max_rent,
        limit=limit,
        skip=skip
    )
    return listings

@router.get("/avg/{locality_id}", response_model=dict)
def get_average_rent(
    locality_id: int,
    property_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get average rent for a locality"""
    avg_rent = RentService.get_avg_rent_by_locality(
        db=db,
        locality_id=locality_id,
        property_type=property_type
    )
    if avg_rent is None:
        raise HTTPException(status_code=404, detail="No listings found for this locality")
    return {"locality_id": locality_id, "property_type": property_type, "avg_rent": avg_rent}

@router.post("/", response_model=RentListingResponse)
def create_rent_listing(
    listing: RentListingCreate,
    db: Session = Depends(get_db)
):
    """Create a new rent listing"""
    return RentService.create_listing(db=db, listing=listing)

@router.post("/scrape/nobroker")
def scrape_nobroker(
    locality: str = Query(...),
    city: str = Query("Bhopal"),
    db: Session = Depends(get_db)
):
    """Trigger NoBroker scraping"""
    listings = RentService.scrape_nobroker(locality=locality, city=city)
    # Save listings to database
    created = []
    for listing_data in listings:
        try:
            listing = RentListingCreate(**listing_data)
            created_listing = RentService.create_listing(db=db, listing=listing)
            created.append(created_listing.id)
        except Exception as e:
            print(f"Error creating listing: {e}")
    return {"scraped": len(listings), "created": len(created), "ids": created}

@router.post("/scrape/olx")
def scrape_olx(
    locality: str = Query(...),
    city: str = Query("Bhopal"),
    db: Session = Depends(get_db)
):
    """Trigger OLX scraping"""
    listings = RentService.scrape_olx(locality=locality, city=city)
    created = []
    for listing_data in listings:
        try:
            listing = RentListingCreate(**listing_data)
            created_listing = RentService.create_listing(db=db, listing=listing)
            created.append(created_listing.id)
        except Exception as e:
            print(f"Error creating listing: {e}")
    return {"scraped": len(listings), "created": len(created), "ids": created}


from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.transport_service import TransportService
from app.schemas.transport import TransportRouteResponse, TransportFareResponse

router = APIRouter(prefix="/transport", tags=["transport"])

@router.get("/routes", response_model=List[TransportRouteResponse])
def get_routes(
    source_locality_id: Optional[int] = Query(None),
    destination_locality_id: Optional[int] = Query(None),
    transport_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get transport routes with optional filters"""
    routes = TransportService.get_routes(
        db=db,
        source_locality_id=source_locality_id,
        destination_locality_id=destination_locality_id,
        transport_type=transport_type
    )
    return routes

@router.get("/routes/{route_id}/fares", response_model=List[TransportFareResponse])
def get_route_fares(
    route_id: int,
    db: Session = Depends(get_db)
):
    """Get fares for a specific route"""
    fares = TransportService.get_route_fares(db=db, route_id=route_id)
    return fares

@router.get("/cost/{source_locality_id}/{destination_locality_id}")
def calculate_monthly_cost(
    source_locality_id: int,
    destination_locality_id: int,
    trips_per_month: int = Query(60, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Calculate monthly transport cost between two localities"""
    cost = TransportService.calculate_monthly_transport_cost(
        db=db,
        source_locality_id=source_locality_id,
        destination_locality_id=destination_locality_id,
        trips_per_month=trips_per_month
    )
    return {
        "source_locality_id": source_locality_id,
        "destination_locality_id": destination_locality_id,
        "trips_per_month": trips_per_month,
        "monthly_cost": cost
    }

@router.post("/fetch/bcll")
def fetch_bcll_fares():
    """Fetch BCLL transport fares"""
    fares = TransportService.fetch_bcll_fares()
    return {"source": "BCLL", "fares_count": len(fares)}


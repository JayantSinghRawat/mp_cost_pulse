from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.geospatial_service import GeospatialService
from app.schemas.geospatial import LocalityResponse, LocalityStatsResponse

router = APIRouter(prefix="/geospatial", tags=["geospatial"])

@router.get("/localities", response_model=List[LocalityResponse])
def get_localities(
    city: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get localities with optional filters"""
    localities = GeospatialService.get_localities(
        db=db,
        city=city,
        district=district
    )
    return localities

@router.get("/localities/{locality_id}/stats", response_model=LocalityStatsResponse)
def get_locality_stats(
    locality_id: int,
    db: Session = Depends(get_db)
):
    """Get statistics for a locality"""
    stats = GeospatialService.get_locality_stats(db=db, locality_id=locality_id)
    if not stats:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No statistics found for this locality")
    return stats

@router.get("/nearby")
def find_nearby_localities(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, ge=0.1, le=50.0),
    db: Session = Depends(get_db)
):
    """Find localities within a radius"""
    localities = GeospatialService.find_nearby_localities(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
    return {"center": {"latitude": latitude, "longitude": longitude}, "radius_km": radius_km, "localities": localities}

@router.get("/heatmap")
def get_heatmap_data(
    data_type: str = Query("rent", regex="^(rent|grocery|transport|cost_burden)$"),
    db: Session = Depends(get_db)
):
    """Generate heatmap data for localities"""
    data = GeospatialService.generate_heatmap_data(db=db, data_type=data_type)
    return {"data_type": data_type, "points": data}

@router.get("/isochrone")
def calculate_isochrone(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    time_minutes: int = Query(30, ge=5, le=120),
    transport_mode: str = Query("driving", regex="^(driving|walking|cycling|transit)$")
):
    """Calculate isochrone (travel time area)"""
    isochrone = GeospatialService.calculate_isochrone(
        latitude=latitude,
        longitude=longitude,
        time_minutes=time_minutes,
        transport_mode=transport_mode
    )
    if not isochrone:
        return {"message": "Isochrone calculation failed or API key not configured"}
    return isochrone

@router.post("/localities/{locality_id}/update-stats", response_model=LocalityStatsResponse)
def update_locality_stats(
    locality_id: int,
    db: Session = Depends(get_db)
):
    """Calculate and update statistics for a locality"""
    stats = GeospatialService.update_locality_stats(db=db, locality_id=locality_id)
    return stats


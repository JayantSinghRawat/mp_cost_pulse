from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.services.inflation_service import InflationService
from app.schemas.inflation import InflationDataResponse

router = APIRouter(prefix="/inflation", tags=["inflation"])

@router.get("/", response_model=List[InflationDataResponse])
def get_inflation_data(
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get inflation data with optional filters"""
    data = InflationService.get_inflation_data(
        db=db,
        category=category,
        source=source,
        start_date=start_date,
        end_date=end_date
    )
    return data

@router.get("/latest", response_model=InflationDataResponse)
def get_latest_inflation(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get the latest inflation data"""
    from fastapi import HTTPException
    data = InflationService.get_latest_inflation(db=db, category=category)
    if not data:
        raise HTTPException(status_code=404, detail="No inflation data found")
    return data

@router.post("/fetch/rbi")
def fetch_rbi_data():
    """Fetch RBI inflation data"""
    data = InflationService.fetch_rbi_data()
    return {"source": "RBI", "records_count": len(data)}

@router.post("/fetch/mp-govt")
def fetch_mp_govt_data():
    """Fetch MP Government inflation data"""
    data = InflationService.fetch_mp_govt_data()
    return {"source": "MP_GOVT", "records_count": len(data)}


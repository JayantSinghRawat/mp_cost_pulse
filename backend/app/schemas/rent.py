from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class RentListingCreate(BaseModel):
    source: str
    title: str
    description: Optional[str] = None
    locality_id: Optional[int] = None
    address: Optional[str] = None
    rent_amount: float
    deposit: Optional[float] = None
    property_type: Optional[str] = None
    area_sqft: Optional[float] = None
    furnished: Optional[str] = None
    available_from: Optional[datetime] = None
    source_url: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RentListingResponse(BaseModel):
    id: int
    source: str
    title: str
    description: Optional[str]
    locality_id: Optional[int]
    address: Optional[str]
    rent_amount: float
    deposit: Optional[float]
    property_type: Optional[str]
    area_sqft: Optional[float]
    furnished: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


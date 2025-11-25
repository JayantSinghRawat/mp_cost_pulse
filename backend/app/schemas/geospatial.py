from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LocalityStatsResponse(BaseModel):
    id: int
    locality_id: int
    avg_rent_1bhk: Optional[float]
    avg_rent_2bhk: Optional[float]
    avg_rent_3bhk: Optional[float]
    avg_grocery_cost_monthly: Optional[float]
    avg_transport_cost_monthly: Optional[float]
    cost_burden_index: Optional[float]
    population_density: Optional[float]
    amenities_score: Optional[float]
    last_updated: datetime
    
    class Config:
        from_attributes = True

class LocalityResponse(BaseModel):
    id: int
    name: str
    city: str
    district: Optional[str]
    state: str
    pincode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    stats: Optional[LocalityStatsResponse] = None
    
    class Config:
        from_attributes = True


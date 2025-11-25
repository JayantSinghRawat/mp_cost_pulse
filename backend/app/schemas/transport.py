from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TransportFareResponse(BaseModel):
    id: int
    route_id: int
    fare_type: str
    fare_amount: float
    valid_from: Optional[datetime]
    
    class Config:
        from_attributes = True

class TransportRouteResponse(BaseModel):
    id: int
    route_number: str
    route_name: Optional[str]
    source_locality_id: Optional[int]
    destination_locality_id: Optional[int]
    transport_type: str
    operator: str
    distance_km: Optional[float]
    duration_minutes: Optional[int]
    fares: List[TransportFareResponse] = []
    
    class Config:
        from_attributes = True


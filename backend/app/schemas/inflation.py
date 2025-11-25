from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class InflationDataResponse(BaseModel):
    id: int
    source: str
    category: Optional[str]
    subcategory: Optional[str]
    value: float
    period: date
    unit: str
    region: str
    
    class Config:
        from_attributes = True


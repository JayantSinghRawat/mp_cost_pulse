from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class GroceryItemResponse(BaseModel):
    id: int
    store_id: int
    name: str
    category: Optional[str]
    brand: Optional[str]
    unit: Optional[str]
    price: float
    quantity: Optional[float]
    image_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class GroceryStoreResponse(BaseModel):
    id: int
    name: str
    locality_id: Optional[int]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    items: List[GroceryItemResponse] = []
    
    class Config:
        from_attributes = True


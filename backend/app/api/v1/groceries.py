from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.grocery_service import GroceryService
from app.schemas.grocery import GroceryStoreResponse, GroceryItemResponse

router = APIRouter(prefix="/groceries", tags=["groceries"])

@router.get("/stores", response_model=List[GroceryStoreResponse])
def get_grocery_stores(
    locality_id: Optional[int] = Query(None),
    store_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get grocery stores with optional filters"""
    stores = GroceryService.get_stores(
        db=db,
        locality_id=locality_id,
        store_name=store_name
    )
    return stores

@router.get("/stores/{store_id}/items", response_model=List[GroceryItemResponse])
def get_store_items(
    store_id: int,
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get items for a specific store"""
    items = GroceryService.get_store_items(
        db=db,
        store_id=store_id,
        category=category
    )
    return items

@router.get("/cost/{locality_id}")
def calculate_monthly_cost(
    locality_id: int,
    db: Session = Depends(get_db)
):
    """Calculate estimated monthly grocery cost for a locality"""
    # Default grocery basket
    default_basket = [
        {"name": "Rice", "quantity": 10, "unit": "kg"},
        {"name": "Wheat", "quantity": 10, "unit": "kg"},
        {"name": "Milk", "quantity": 30, "unit": "liter"},
        {"name": "Eggs", "quantity": 30, "unit": "dozen"},
        {"name": "Vegetables", "quantity": 30, "unit": "kg"},
        {"name": "Fruits", "quantity": 15, "unit": "kg"},
    ]
    
    cost = GroceryService.calculate_monthly_grocery_cost(
        db=db,
        locality_id=locality_id,
        items=default_basket
    )
    return {"locality_id": locality_id, "monthly_cost": cost, "basket": default_basket}

@router.post("/fetch/bigbasket")
def fetch_bigbasket(
    locality: str = Query(...),
    city: str = Query("Bhopal")
):
    """Fetch products from BigBasket API"""
    products = GroceryService.fetch_bigbasket_products(locality=locality, city=city)
    return {"source": "BigBasket", "locality": locality, "products_count": len(products)}

@router.post("/fetch/blinkit")
def fetch_blinkit(
    locality: str = Query(...),
    city: str = Query("Bhopal")
):
    """Fetch products from Blinkit API"""
    products = GroceryService.fetch_blinkit_products(locality=locality, city=city)
    return {"source": "Blinkit", "locality": locality, "products_count": len(products)}


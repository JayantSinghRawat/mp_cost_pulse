from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.grocery import GroceryStore, GroceryItem
from app.models.geospatial import Locality
import requests
from app.core.config import settings

class GroceryService:
    @staticmethod
    def get_stores(
        db: Session,
        locality_id: Optional[int] = None,
        store_name: Optional[str] = None
    ) -> List[GroceryStore]:
        """Get grocery stores with filters"""
        query = db.query(GroceryStore).filter(GroceryStore.is_active == "active")
        
        if locality_id:
            query = query.filter(GroceryStore.locality_id == locality_id)
        if store_name:
            query = query.filter(GroceryStore.name == store_name)
        
        return query.all()
    
    @staticmethod
    def get_store_items(
        db: Session,
        store_id: int,
        category: Optional[str] = None
    ) -> List[GroceryItem]:
        """Get items for a specific store"""
        query = db.query(GroceryItem).filter(GroceryItem.store_id == store_id)
        
        if category:
            query = query.filter(GroceryItem.category == category)
        
        return query.all()
    
    @staticmethod
    def fetch_bigbasket_products(locality: str, city: str = "Bhopal") -> List[dict]:
        """Fetch products from BigBasket API"""
        products = []
        try:
            # BigBasket API integration
            # This is a placeholder - actual implementation would use their API
            api_key = settings.BIGBASKET_API_KEY
            if not api_key:
                return products
            
            # Example API call structure
            # url = f"https://api.bigbasket.com/v1/products"
            # headers = {"Authorization": f"Bearer {api_key}"}
            # params = {"locality": locality, "city": city}
            # response = requests.get(url, headers=headers, params=params)
            # if response.status_code == 200:
            #     products = response.json().get("products", [])
        except Exception as e:
            print(f"Error fetching BigBasket products: {e}")
        
        return products
    
    @staticmethod
    def fetch_blinkit_products(locality: str, city: str = "Bhopal") -> List[dict]:
        """Fetch products from Blinkit API"""
        products = []
        try:
            # Blinkit API integration
            api_key = settings.BLINKIT_API_KEY
            if not api_key:
                return products
            
            # Example API call structure
            # url = f"https://api.blinkit.com/v1/products"
            # headers = {"Authorization": f"Bearer {api_key}"}
            # params = {"locality": locality, "city": city}
            # response = requests.get(url, headers=headers, params=params)
        except Exception as e:
            print(f"Error fetching Blinkit products: {e}")
        
        return products
    
    @staticmethod
    def calculate_monthly_grocery_cost(
        db: Session,
        locality_id: int,
        items: List[dict]  # List of {item_name, quantity, unit}
    ) -> float:
        """Calculate monthly grocery cost for a locality"""
        stores = db.query(GroceryStore).filter(
            GroceryStore.locality_id == locality_id,
            GroceryStore.is_active == "active"
        ).all()
        
        if not stores:
            return 0.0
        
        total_cost = 0.0
        for item_req in items:
            item_name = item_req.get("name", "").lower()
            quantity = item_req.get("quantity", 1)
            
            # Find the item in stores
            for store in stores:
                items_in_store = db.query(GroceryItem).filter(
                    GroceryItem.store_id == store.id,
                    GroceryItem.name.ilike(f"%{item_name}%")
                ).first()
                
                if items_in_store:
                    total_cost += items_in_store.price * quantity
                    break
        
        return total_cost


from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional, Dict
from app.models.geospatial import Locality, LocalityStats
from app.models.rent import RentListing
from app.models.grocery import GroceryStore, GroceryItem
from app.models.transport import TransportRoute, TransportFare
import requests
from app.core.config import settings

class GeospatialService:
    @staticmethod
    def get_localities(
        db: Session,
        city: Optional[str] = None,
        district: Optional[str] = None
    ) -> List[Locality]:
        """Get localities with filters"""
        query = db.query(Locality)
        
        if city:
            query = query.filter(Locality.city == city)
        if district:
            query = query.filter(Locality.district == district)
        
        return query.all()
    
    @staticmethod
    def get_locality_stats(
        db: Session,
        locality_id: int
    ) -> Optional[LocalityStats]:
        """Get statistics for a locality"""
        return db.query(LocalityStats).filter(
            LocalityStats.locality_id == locality_id
        ).first()
    
    @staticmethod
    def find_nearby_localities(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0
    ) -> List[Dict]:
        """Find localities within a radius using PostGIS"""
        # Convert radius from km to degrees (approximate)
        radius_deg = radius_km / 111.0
        
        query = text("""
            SELECT id, name, city, latitude, longitude,
                   ST_Distance(
                       geometry,
                       ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                   ) / 1000.0 as distance_km
            FROM localities
            WHERE ST_DWithin(
                geometry::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius * 1000
            )
            ORDER BY distance_km
        """)
        
        result = db.execute(
            query,
            {"lat": latitude, "lon": longitude, "radius": radius_km}
        )
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "city": row[2],
                "latitude": row[3],
                "longitude": row[4],
                "distance_km": row[5]
            }
            for row in result
        ]
    
    @staticmethod
    def generate_heatmap_data(
        db: Session,
        data_type: str = "rent"  # 'rent', 'grocery', 'transport', 'cost_burden'
    ) -> List[Dict]:
        """Generate heatmap data for localities"""
        if data_type == "rent":
            query = text("""
                SELECT 
                    l.id,
                    l.name,
                    l.latitude,
                    l.longitude,
                    AVG(r.rent_amount) as avg_rent,
                    COUNT(r.id) as listing_count
                FROM localities l
                LEFT JOIN rent_listings r ON l.id = r.locality_id
                WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
                GROUP BY l.id, l.name, l.latitude, l.longitude
                HAVING COUNT(r.id) > 0
            """)
            result = db.execute(query)
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "latitude": float(row[2]) if row[2] else None,
                    "longitude": float(row[3]) if row[3] else None,
                    "value": float(row[4]) if row[4] else None,
                    "metadata": {"listing_count": int(row[5]) if row[5] else 0}
                }
                for row in result
            ]
        elif data_type == "cost_burden":
            query = text("""
                SELECT 
                    l.id,
                    l.name,
                    l.latitude,
                    l.longitude,
                    ls.cost_burden_index,
                    ls.avg_rent_2bhk,
                    ls.avg_grocery_cost_monthly,
                    ls.avg_transport_cost_monthly
                FROM localities l
                LEFT JOIN locality_stats ls ON l.id = ls.locality_id
                WHERE l.latitude IS NOT NULL 
                  AND l.longitude IS NOT NULL
                  AND ls.cost_burden_index IS NOT NULL
            """)
            result = db.execute(query)
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "latitude": float(row[2]) if row[2] else None,
                    "longitude": float(row[3]) if row[3] else None,
                    "value": float(row[4]) if row[4] else None,
                    "metadata": {
                        "avg_rent_2bhk": float(row[5]) if row[5] else None,
                        "avg_grocery_cost": float(row[6]) if row[6] else None,
                        "avg_transport_cost": float(row[7]) if row[7] else None,
                    }
                }
                for row in result
            ]
        else:
            return []
    
    @staticmethod
    def calculate_isochrone(
        latitude: float,
        longitude: float,
        time_minutes: int = 30,
        transport_mode: str = "driving"
    ) -> Optional[Dict]:
        """Calculate isochrone using external API"""
        try:
            api_key = settings.ISOCRONE_API_KEY
            if not api_key:
                return None
            
            # Example using OpenRouteService or similar
            # url = "https://api.openrouteservice.org/v2/isochrones/driving"
            # headers = {"Authorization": f"Bearer {api_key}"}
            # params = {
            #     "locations": [[longitude, latitude]],
            #     "range": [time_minutes * 60],  # Convert to seconds
            #     "range_type": "time"
            # }
            # response = requests.post(url, json=params, headers=headers)
            # if response.status_code == 200:
            #     return response.json()
        except Exception as e:
            print(f"Error calculating isochrone: {e}")
        
        return None
    
    @staticmethod
    def update_locality_stats(db: Session, locality_id: int) -> LocalityStats:
        """Calculate and update statistics for a locality"""
        from app.services.rent_service import RentService
        from app.services.grocery_service import GroceryService
        from app.services.transport_service import TransportService
        
        # Calculate average rents
        avg_rent_1bhk = RentService.get_avg_rent_by_locality(db, locality_id, "1BHK")
        avg_rent_2bhk = RentService.get_avg_rent_by_locality(db, locality_id, "2BHK")
        avg_rent_3bhk = RentService.get_avg_rent_by_locality(db, locality_id, "3BHK")
        
        # Calculate grocery cost from scraped data
        stores = GroceryService.get_stores(db, locality_id=locality_id)
        avg_grocery_cost = 0.0
        if stores:
            # Use actual scraped grocery items to calculate monthly cost
            # Standard monthly grocery basket
            monthly_basket = [
                {"name": "Rice", "quantity": 10, "unit": "kg"},
                {"name": "Wheat", "quantity": 10, "unit": "kg"},
                {"name": "Milk", "quantity": 30, "unit": "liter"},
                {"name": "Eggs", "quantity": 30, "unit": "dozen"},
                {"name": "Onion", "quantity": 5, "unit": "kg"},
                {"name": "Potato", "quantity": 5, "unit": "kg"},
                {"name": "Tomato", "quantity": 5, "unit": "kg"},
                {"name": "Cooking Oil", "quantity": 2, "unit": "liter"},
            ]
            
            # Calculate using actual scraped prices
            avg_grocery_cost = GroceryService.calculate_monthly_grocery_cost(
                db, locality_id, monthly_basket
            )
            
            # If no scraped data, use average price estimate
            if avg_grocery_cost == 0:
                total_items = db.query(GroceryItem).filter(
                    GroceryItem.store_id.in_([s.id for s in stores])
                ).count()
                if total_items > 0:
                    avg_price = db.query(func.avg(GroceryItem.price)).filter(
                        GroceryItem.store_id.in_([s.id for s in stores])
                    ).scalar()
                    # Estimate: avg_price * typical monthly quantity (50 items)
                    avg_grocery_cost = (avg_price or 0) * 50
        
        # Calculate transport cost (simplified)
        avg_transport_cost = 2000.0  # Placeholder
        
        # Calculate cost burden index (rent + groceries + transport as % of income)
        # Assuming average income of 50,000 INR
        avg_income = 50000.0
        total_monthly_cost = (avg_rent_2bhk or 0) + avg_grocery_cost + avg_transport_cost
        cost_burden_index = (total_monthly_cost / avg_income) * 100 if avg_income > 0 else 0
        
        # Get or create stats
        stats = db.query(LocalityStats).filter(
            LocalityStats.locality_id == locality_id
        ).first()
        
        if not stats:
            stats = LocalityStats(locality_id=locality_id)
            db.add(stats)
        
        stats.avg_rent_1bhk = avg_rent_1bhk
        stats.avg_rent_2bhk = avg_rent_2bhk
        stats.avg_rent_3bhk = avg_rent_3bhk
        stats.avg_grocery_cost_monthly = avg_grocery_cost
        stats.avg_transport_cost_monthly = avg_transport_cost
        stats.cost_burden_index = cost_burden_index
        
        db.commit()
        db.refresh(stats)
        
        return stats


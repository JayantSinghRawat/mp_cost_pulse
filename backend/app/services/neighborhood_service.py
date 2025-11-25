"""
Service to aggregate and store neighborhood data from various sources
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.neighborhood import NeighborhoodData
from app.models.geospatial import Locality
from app.models.rent import RentListing
from app.models.grocery import GroceryStore
from app.services.scraping_service import (
    AQIScrapingService,
    DeliveryAvailabilityService,
    HygieneIndicatorService,
    AmenitiesService,
    GroceryStoresService
)
from app.services.rent_service import RentService
from app.services.grocery_service import GroceryService

class NeighborhoodService:
    """Service to aggregate and manage neighborhood data"""
    
    @staticmethod
    def aggregate_neighborhood_data(
        db: Session,
        locality_id: int,
        city: str
    ) -> Optional[NeighborhoodData]:
        """
        Aggregate all data for a neighborhood and store in NeighborhoodData
        """
        # Get locality
        locality = db.query(Locality).filter(Locality.id == locality_id).first()
        if not locality or not locality.latitude or not locality.longitude:
            return None
        
        latitude = locality.latitude
        longitude = locality.longitude
        
        # Get or create neighborhood data record
        neighborhood_data = db.query(NeighborhoodData).filter(
            NeighborhoodData.locality_id == locality_id
        ).first()
        
        if not neighborhood_data:
            neighborhood_data = NeighborhoodData(
                locality_id=locality_id,
                city=city
            )
            db.add(neighborhood_data)
        
        # 1. Aggregate rent prices
        avg_rent_1bhk = RentService.get_avg_rent_by_locality(db, locality_id, '1BHK')
        avg_rent_2bhk = RentService.get_avg_rent_by_locality(db, locality_id, '2BHK')
        avg_rent_3bhk = RentService.get_avg_rent_by_locality(db, locality_id, '3BHK')
        
        rent_count = db.query(RentListing).filter(
            RentListing.locality_id == locality_id
        ).count()
        
        neighborhood_data.avg_rent_1bhk = avg_rent_1bhk
        neighborhood_data.avg_rent_2bhk = avg_rent_2bhk
        neighborhood_data.avg_rent_3bhk = avg_rent_3bhk
        neighborhood_data.rent_listings_count = rent_count
        
        # 2. Aggregate grocery costs
        # First try database stores
        grocery_stores = db.query(GroceryStore).filter(
            GroceryStore.locality_id == locality_id
        ).all()
        
        # Also fetch from Google Places API for more accurate count
        grocery_places_data = GroceryStoresService.get_nearby_grocery_stores(
            latitude, longitude, city, radius_km=2.0
        )
        
        # Use Google Places count if available and higher, otherwise use database count
        places_count = grocery_places_data.get('grocery_stores_count', 0)
        db_count = len(grocery_stores)
        neighborhood_data.grocery_stores_count = max(places_count, db_count) if places_count > 0 else db_count
        
        # Calculate average monthly grocery cost from database items
        from app.models.grocery import GroceryItem
        from sqlalchemy import func
        
        if grocery_stores:
            # Calculate from actual scraped grocery items
            monthly_basket = [
                {"name": "Rice", "quantity": 10},
                {"name": "Wheat", "quantity": 10},
                {"name": "Milk", "quantity": 30},
                {"name": "Eggs", "quantity": 30},
                {"name": "Onion", "quantity": 5},
                {"name": "Potato", "quantity": 5},
                {"name": "Tomato", "quantity": 5},
                {"name": "Cooking Oil", "quantity": 2},
            ]
            grocery_cost = GroceryService.calculate_monthly_grocery_cost(
                db, locality_id, monthly_basket
            )
            neighborhood_data.avg_grocery_cost_monthly = grocery_cost if grocery_cost > 0 else None
        else:
            neighborhood_data.avg_grocery_cost_monthly = None
        
        # 3. Get delivery availability
        delivery_data = DeliveryAvailabilityService.get_all_delivery_services(
            latitude, longitude, city
        )
        
        neighborhood_data.blinkit_available = delivery_data.get('blinkit', {}).get('available', False)
        neighborhood_data.zomato_available = delivery_data.get('zomato', {}).get('available', False)
        neighborhood_data.swiggy_available = delivery_data.get('swiggy', {}).get('available', False)
        neighborhood_data.delivery_services = delivery_data
        
        # 4. Get AQI data
        aqi_data = AQIScrapingService.get_aqi_by_location(latitude, longitude, city)
        neighborhood_data.aqi_value = aqi_data.get('aqi_value')
        neighborhood_data.aqi_category = aqi_data.get('aqi_category')
        neighborhood_data.aqi_pm25 = aqi_data.get('aqi_pm25')
        neighborhood_data.aqi_pm10 = aqi_data.get('aqi_pm10')
        neighborhood_data.aqi_no2 = aqi_data.get('aqi_no2')
        
        # 5. Get hygiene indicators (restaurant ratings) - Use Google Places API
        hygiene_data = HygieneIndicatorService.get_restaurant_ratings(
            latitude, longitude, city, radius_km=2.0
        )
        neighborhood_data.avg_restaurant_rating = hygiene_data.get('avg_restaurant_rating')
        neighborhood_data.restaurants_count = hygiene_data.get('restaurants_count', 0)
        neighborhood_data.highly_rated_restaurants_count = hygiene_data.get('highly_rated_restaurants_count', 0)
        
        # 6. Get amenities
        amenities_data = AmenitiesService.get_nearby_amenities(
            latitude, longitude, city
        )
        neighborhood_data.hospitals_count = amenities_data.get('hospitals_count', 0)
        neighborhood_data.schools_count = amenities_data.get('schools_count', 0)
        neighborhood_data.parks_count = amenities_data.get('parks_count', 0)
        neighborhood_data.shopping_malls_count = amenities_data.get('shopping_malls_count', 0)
        neighborhood_data.metro_stations_count = amenities_data.get('metro_stations_count', 0)
        neighborhood_data.bus_stops_count = amenities_data.get('bus_stops_count', 0)
        neighborhood_data.amenities = amenities_data
        
        # 7. Calculate scores
        neighborhood_data.safety_score = NeighborhoodService._calculate_safety_score(neighborhood_data)
        neighborhood_data.connectivity_score = NeighborhoodService._calculate_connectivity_score(neighborhood_data)
        neighborhood_data.amenities_score = NeighborhoodService._calculate_amenities_score(neighborhood_data)
        
        # 8. Store metadata
        neighborhood_data.last_scraped_at = datetime.utcnow()
        neighborhood_data.data_source = {
            'aqi_source': aqi_data.get('source'),
            'delivery_source': delivery_data.get('blinkit', {}).get('source'),
            'hygiene_source': hygiene_data.get('source'),
            'amenities_source': amenities_data.get('source'),
            'scraped_at': datetime.utcnow().isoformat()
        }
        
        db.commit()
        db.refresh(neighborhood_data)
        
        return neighborhood_data
    
    @staticmethod
    def _calculate_safety_score(neighborhood_data: NeighborhoodData) -> float:
        """Calculate safety score (0-10) based on AQI and other factors"""
        score = 10.0
        
        # Penalize for poor AQI
        if neighborhood_data.aqi_value:
            if neighborhood_data.aqi_value > 200:
                score -= 4.0
            elif neighborhood_data.aqi_value > 150:
                score -= 2.5
            elif neighborhood_data.aqi_value > 100:
                score -= 1.0
        
        # Bonus for good restaurant hygiene
        if neighborhood_data.avg_restaurant_rating:
            if neighborhood_data.avg_restaurant_rating >= 4.5:
                score += 0.5
            elif neighborhood_data.avg_restaurant_rating < 3.0:
                score -= 1.0
        
        return max(0.0, min(10.0, score))
    
    @staticmethod
    def _calculate_connectivity_score(neighborhood_data: NeighborhoodData) -> float:
        """Calculate connectivity score (0-10) based on transport options"""
        score = 0.0
        
        # Metro stations
        if neighborhood_data.metro_stations_count:
            score += min(3.0, neighborhood_data.metro_stations_count * 1.0)
        
        # Bus stops
        if neighborhood_data.bus_stops_count:
            score += min(3.0, neighborhood_data.bus_stops_count * 0.1)
        
        # Delivery services (indicates good connectivity)
        delivery_count = sum([
            neighborhood_data.blinkit_available,
            neighborhood_data.zomato_available,
            neighborhood_data.swiggy_available
        ])
        score += delivery_count * 1.0
        
        return min(10.0, score)
    
    @staticmethod
    def _calculate_amenities_score(neighborhood_data: NeighborhoodData) -> float:
        """Calculate amenities score (0-10)"""
        score = 0.0
        
        # Hospitals
        if neighborhood_data.hospitals_count:
            score += min(2.0, neighborhood_data.hospitals_count * 0.5)
        
        # Schools
        if neighborhood_data.schools_count:
            score += min(2.0, neighborhood_data.schools_count * 0.2)
        
        # Parks
        if neighborhood_data.parks_count:
            score += min(2.0, neighborhood_data.parks_count * 0.3)
        
        # Shopping malls
        if neighborhood_data.shopping_malls_count:
            score += min(2.0, neighborhood_data.shopping_malls_count * 1.0)
        
        # Restaurants
        if neighborhood_data.restaurants_count:
            score += min(2.0, neighborhood_data.restaurants_count * 0.1)
        
        return min(10.0, score)
    
    @staticmethod
    def get_neighborhood_data(
        db: Session,
        locality_id: int
    ) -> Optional[NeighborhoodData]:
        """Get neighborhood data for a locality"""
        return db.query(NeighborhoodData).filter(
            NeighborhoodData.locality_id == locality_id
        ).first()
    
    @staticmethod
    def get_all_neighborhoods_by_city(
        db: Session,
        city: str
    ) -> List[NeighborhoodData]:
        """Get all neighborhood data for a city"""
        return db.query(NeighborhoodData).filter(
            NeighborhoodData.city == city
        ).all()
    
    @staticmethod
    def refresh_neighborhood_data(
        db: Session,
        locality_id: int,
        city: str
    ) -> Optional[NeighborhoodData]:
        """Refresh/update neighborhood data by re-scraping"""
        return NeighborhoodService.aggregate_neighborhood_data(db, locality_id, city)


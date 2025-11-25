from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.transport import TransportRoute, TransportFare
from app.models.geospatial import Locality
import requests

class TransportService:
    @staticmethod
    def get_routes(
        db: Session,
        source_locality_id: Optional[int] = None,
        destination_locality_id: Optional[int] = None,
        transport_type: Optional[str] = None
    ) -> List[TransportRoute]:
        """Get transport routes with filters"""
        query = db.query(TransportRoute).filter(TransportRoute.is_active == "active")
        
        if source_locality_id:
            query = query.filter(TransportRoute.source_locality_id == source_locality_id)
        if destination_locality_id:
            query = query.filter(TransportRoute.destination_locality_id == destination_locality_id)
        if transport_type:
            query = query.filter(TransportRoute.transport_type == transport_type)
        
        return query.all()
    
    @staticmethod
    def get_route_fares(
        db: Session,
        route_id: int
    ) -> List[TransportFare]:
        """Get fares for a specific route"""
        return db.query(TransportFare).filter(
            TransportFare.route_id == route_id
        ).all()
    
    @staticmethod
    def fetch_bcll_fares() -> List[dict]:
        """Fetch BCLL (Bhopal City Link Limited) transport fares"""
        fares = []
        try:
            # BCLL API or scraping logic
            # This is a placeholder - actual implementation would use their API
            # url = "https://bcll.bhopal.gov.in/api/fares"
            # response = requests.get(url, timeout=10)
            # if response.status_code == 200:
            #     fares = response.json().get("fares", [])
            pass
        except Exception as e:
            print(f"Error fetching BCLL fares: {e}")
        
        return fares
    
    @staticmethod
    def calculate_monthly_transport_cost(
        db: Session,
        source_locality_id: int,
        destination_locality_id: int,
        trips_per_month: int = 60  # 2 trips per day * 30 days
    ) -> float:
        """Calculate monthly transport cost between two localities"""
        route = db.query(TransportRoute).filter(
            TransportRoute.source_locality_id == source_locality_id,
            TransportRoute.destination_locality_id == destination_locality_id,
            TransportRoute.is_active == "active"
        ).first()
        
        if not route:
            return 0.0
        
        # Get the current fare
        fare = db.query(TransportFare).filter(
            TransportFare.route_id == route.id,
            TransportFare.fare_type == "Regular"
        ).order_by(TransportFare.valid_from.desc()).first()
        
        if not fare:
            return 0.0
        
        return fare.fare_amount * trips_per_month


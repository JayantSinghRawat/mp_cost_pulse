from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class NeighborhoodData(Base):
    """Aggregated data for a neighborhood/locality"""
    __tablename__ = "neighborhood_data"
    
    id = Column(Integer, primary_key=True, index=True)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    
    # Rent prices (average by property type)
    avg_rent_1bhk = Column(Float)
    avg_rent_2bhk = Column(Float)
    avg_rent_3bhk = Column(Float)
    rent_listings_count = Column(Integer, default=0)
    
    # Food & grocery costs
    avg_grocery_cost_monthly = Column(Float)  # Average monthly grocery cost for a family
    grocery_stores_count = Column(Integer, default=0)
    
    # Delivery availability
    blinkit_available = Column(Boolean, default=False)
    zomato_available = Column(Boolean, default=False)
    swiggy_available = Column(Boolean, default=False)
    delivery_services = Column(JSONB)  # Store detailed delivery service data
    
    # AQI (Air Quality Index)
    aqi_value = Column(Float)  # Current AQI
    aqi_category = Column(String)  # 'Good', 'Moderate', 'Unhealthy', etc.
    aqi_pm25 = Column(Float)
    aqi_pm10 = Column(Float)
    aqi_no2 = Column(Float)
    
    # Hygiene indicators (restaurant ratings)
    avg_restaurant_rating = Column(Float)  # Average rating of restaurants in area
    restaurants_count = Column(Integer, default=0)
    highly_rated_restaurants_count = Column(Integer, default=0)  # 4+ stars
    
    # Amenities and nearby services
    amenities = Column(JSONB)  # Store amenities like hospitals, schools, parks, etc.
    hospitals_count = Column(Integer, default=0)
    schools_count = Column(Integer, default=0)
    parks_count = Column(Integer, default=0)
    shopping_malls_count = Column(Integer, default=0)
    metro_stations_count = Column(Integer, default=0)
    bus_stops_count = Column(Integer, default=0)
    
    # Additional metrics
    safety_score = Column(Float)  # Calculated safety score (0-10)
    connectivity_score = Column(Float)  # Transport connectivity score (0-10)
    amenities_score = Column(Float)  # Overall amenities score (0-10)
    
    # Metadata
    last_scraped_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    data_source = Column(JSONB)  # Store source URLs and timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    locality = relationship("Locality", backref="neighborhood_data")


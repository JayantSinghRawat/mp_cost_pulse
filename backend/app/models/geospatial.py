from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Locality(Base):
    __tablename__ = "localities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    city = Column(String, default="Bhopal")
    district = Column(String)
    state = Column(String, default="Madhya Pradesh")
    pincode = Column(String)
    geometry = Column(Geometry('POINT', srid=4326))  # PostGIS geometry
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    rent_listings = relationship("RentListing", back_populates="locality")
    grocery_stores = relationship("GroceryStore", back_populates="locality")
    stats = relationship("LocalityStats", back_populates="locality", uselist=False)

class LocalityStats(Base):
    __tablename__ = "locality_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    locality_id = Column(Integer, ForeignKey("localities.id"), unique=True)
    avg_rent_1bhk = Column(Float)
    avg_rent_2bhk = Column(Float)
    avg_rent_3bhk = Column(Float)
    avg_grocery_cost_monthly = Column(Float)
    avg_transport_cost_monthly = Column(Float)
    cost_burden_index = Column(Float)  # Calculated index
    population_density = Column(Float)
    amenities_score = Column(Float)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    locality = relationship("Locality", back_populates="stats")


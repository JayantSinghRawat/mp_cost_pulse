from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class TransportRoute(Base):
    __tablename__ = "transport_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route_number = Column(String, nullable=False)
    route_name = Column(String)
    source_locality_id = Column(Integer, ForeignKey("localities.id"))
    destination_locality_id = Column(Integer, ForeignKey("localities.id"))
    transport_type = Column(String)  # 'Bus', 'Metro', 'Auto', etc.
    operator = Column(String, default="BCLL")  # BCLL for buses
    distance_km = Column(Float)
    duration_minutes = Column(Integer)
    is_active = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    source_locality = relationship("Locality", foreign_keys=[source_locality_id])
    destination_locality = relationship("Locality", foreign_keys=[destination_locality_id])
    fares = relationship("TransportFare", back_populates="route")

class TransportFare(Base):
    __tablename__ = "transport_fares"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("transport_routes.id"))
    fare_type = Column(String)  # 'Regular', 'AC', 'Student', etc.
    fare_amount = Column(Float, nullable=False)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    route = relationship("TransportRoute", back_populates="fares")


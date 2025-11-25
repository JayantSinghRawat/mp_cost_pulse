from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class RentListing(Base):
    __tablename__ = "rent_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # 'nobroker' or 'olx'
    title = Column(String, nullable=False)
    description = Column(Text)
    locality_id = Column(Integer, ForeignKey("localities.id"))
    address = Column(String)
    rent_amount = Column(Float, nullable=False)
    deposit = Column(Float)
    property_type = Column(String)  # '1BHK', '2BHK', '3BHK', etc.
    area_sqft = Column(Float)
    furnished = Column(String)  # 'Fully Furnished', 'Semi Furnished', 'Unfurnished'
    available_from = Column(DateTime)
    source_url = Column(String, unique=True)
    source_data = Column(JSONB)  # Store raw scraped data
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    locality = relationship("Locality", back_populates="rent_listings")


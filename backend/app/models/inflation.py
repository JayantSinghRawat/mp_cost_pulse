from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func
from app.core.database import Base

class InflationData(Base):
    __tablename__ = "inflation_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # 'RBI' or 'MP_GOVT'
    category = Column(String)  # 'Food', 'Housing', 'Transport', 'Overall', etc.
    subcategory = Column(String)  # More specific category
    value = Column(Float, nullable=False)  # Inflation percentage
    period = Column(Date, nullable=False)  # Year-Month
    unit = Column(String, default="percentage")
    region = Column(String, default="MP")  # Madhya Pradesh
    extra_data = Column(String)  # Additional JSON data as string
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


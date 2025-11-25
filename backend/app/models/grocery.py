from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class GroceryStore(Base):
    __tablename__ = "grocery_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 'BigBasket', 'Blinkit', etc.
    store_id = Column(String, unique=True)  # Store ID from API
    locality_id = Column(Integer, ForeignKey("localities.id"))
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    is_active = Column(String, default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    locality = relationship("Locality", back_populates="grocery_stores")
    items = relationship("GroceryItem", back_populates="store")

class GroceryItem(Base):
    __tablename__ = "grocery_items"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("grocery_stores.id"))
    name = Column(String, nullable=False)
    category = Column(String)  # 'Vegetables', 'Fruits', 'Dairy', etc.
    brand = Column(String)
    unit = Column(String)  # 'kg', 'pack', 'dozen', etc.
    price = Column(Float, nullable=False)
    quantity = Column(Float)
    product_id = Column(String)  # Product ID from API
    image_url = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    store = relationship("GroceryStore", back_populates="items")


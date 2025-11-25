from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with PostGIS extension and create all tables"""
    from sqlalchemy import text
    # Import all models to ensure they're registered
    from app.models import (
        User, RentListing, GroceryStore, GroceryItem, 
        TransportRoute, TransportFare, InflationData, 
        Locality, LocalityStats, MLModelVersion, Prediction, OTP, NeighborhoodData
    )
    
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


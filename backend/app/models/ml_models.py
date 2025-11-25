from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MLModelVersion(Base):
    __tablename__ = "ml_model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False, index=True)  # 'cost_predictor' or 'rent_classifier'
    version = Column(String, nullable=False)  # e.g., 'v1.0.0'
    model_path = Column(String, nullable=False)  # Path to saved model file
    metrics = Column(JSON)  # Training metrics (accuracy, mse, etc.)
    training_data_hash = Column(String)  # Hash of training data for reproducibility
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    model_metadata = Column(JSON)  # Additional model metadata (renamed from metadata to avoid SQLAlchemy conflict)

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_name = Column(String, nullable=False)
    model_version = Column(String)
    input_data = Column(JSON, nullable=False)  # Input features
    prediction = Column(JSON, nullable=False)  # Prediction result
    confidence = Column(Float)  # Prediction confidence score
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", backref="predictions")


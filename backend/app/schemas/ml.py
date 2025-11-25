from pydantic import BaseModel, Field
from typing import Dict

class CostPredictionRequest(BaseModel):
    """Request schema for cost prediction"""
    user_profile: Dict = Field(..., description="User profile with income, family_size, etc.")
    locality_id: int = Field(..., description="Locality ID for prediction")

class CostPredictionResponse(BaseModel):
    """Response schema for cost prediction"""
    predicted_monthly_cost: float
    breakdown: Dict
    confidence: float
    model_available: bool


from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class RecommendationRequest(BaseModel):
    """Request schema for neighborhood recommendations"""
    city: str = Field(..., description="City name")
    number_of_people: int = Field(..., ge=1, le=10, description="Number of people in household")
    max_travel_distance_km: float = Field(..., ge=0, le=50, description="Maximum travel distance in km")
    budget: float = Field(..., ge=0, description="Monthly budget in INR")
    property_type: str = Field(default="2BHK", description="Property type: 1BHK, 2BHK, or 3BHK")
    weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional weights for factors (rent, grocery_cost, delivery_availability, aqi, hygiene, amenities, connectivity)"
    )
    top_n: int = Field(default=10, ge=1, le=50, description="Number of top recommendations to return")

class RecommendationResponse(BaseModel):
    """Response schema for a single neighborhood recommendation"""
    neighborhood_id: int
    locality_id: int
    locality_name: str
    city: str
    score: float
    rent: float
    grocery_cost: Optional[float] = None
    total_monthly_cost: float
    aqi: float
    aqi_category: Optional[str]
    hygiene_rating: Optional[float] = None
    amenities_score: float
    connectivity_score: float
    delivery_services: Dict[str, bool]
    amenities: Dict[str, int]
    # Food and restaurant data
    restaurants_count: Optional[int] = 0
    highly_rated_restaurants: Optional[int] = 0
    avg_restaurant_rating: Optional[float] = None
    grocery_stores_count: Optional[int] = 0
    latitude: Optional[float]
    longitude: Optional[float]
    normalized_scores: Dict[str, float]

class RecommendationsResponse(BaseModel):
    """Response schema for recommendations list"""
    recommendations: List[RecommendationResponse]
    total_neighborhoods: int
    filters_applied: Dict


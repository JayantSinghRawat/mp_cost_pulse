from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationsResponse
)
from app.services.recommendation_service import RecommendationService
from app.services.neighborhood_service import NeighborhoodService
from app.models.geospatial import Locality

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.post("/neighborhoods", response_model=RecommendationsResponse)
def get_neighborhood_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get neighborhood recommendations based on user parameters
    
    - **city**: City name
    - **number_of_people**: Number of people in household
    - **max_travel_distance_km**: Maximum travel distance preference
    - **budget**: Monthly budget in INR
    - **property_type**: Property type (1BHK, 2BHK, 3BHK)
    - **weights**: Optional weights for different factors
    - **top_n**: Number of top recommendations to return
    """
    try:
        recommendations = RecommendationService.get_top_recommendations(
            db=db,
            city=request.city,
            number_of_people=request.number_of_people,
            max_travel_distance_km=request.max_travel_distance_km,
            budget=request.budget,
            weights=request.weights,
            property_type=request.property_type,
            top_n=request.top_n
        )
        
        return RecommendationsResponse(
            recommendations=recommendations,
            total_neighborhoods=len(recommendations),
            filters_applied={
                'city': request.city,
                'number_of_people': request.number_of_people,
                'max_travel_distance_km': request.max_travel_distance_km,
                'budget': request.budget,
                'property_type': request.property_type,
                'weights': request.weights or {}
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.post("/aggregate/{locality_id}")
def aggregate_neighborhood_data(
    locality_id: int,
    city: str,
    db: Session = Depends(get_db)
):
    """
    Trigger aggregation of neighborhood data for a specific locality
    This scrapes and aggregates all data sources
    """
    try:
        neighborhood_data = NeighborhoodService.aggregate_neighborhood_data(
            db=db,
            locality_id=locality_id,
            city=city
        )
        
        if not neighborhood_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Locality not found"
            )
        
        return {
            "message": "Neighborhood data aggregated successfully",
            "neighborhood_id": neighborhood_data.id,
            "locality_id": neighborhood_data.locality_id,
            "last_scraped_at": neighborhood_data.last_scraped_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error aggregating data: {str(e)}"
        )

@router.post("/refresh/{city}")
def refresh_city_neighborhoods(
    city: str,
    db: Session = Depends(get_db)
):
    """
    Refresh all neighborhood data for a city
    This re-scrapes and aggregates data for all localities in the city
    """
    try:
        # Get all localities for the city
        localities = db.query(Locality).filter(Locality.city == city).all()
        
        if not localities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No localities found for city: {city}"
            )
        
        refreshed = []
        errors = []
        
        for locality in localities:
            try:
                neighborhood_data = NeighborhoodService.refresh_neighborhood_data(
                    db=db,
                    locality_id=locality.id,
                    city=city
                )
                if neighborhood_data:
                    refreshed.append(locality.id)
            except Exception as e:
                errors.append({
                    'locality_id': locality.id,
                    'locality_name': locality.name,
                    'error': str(e)
                })
        
        return {
            "message": f"Refreshed {len(refreshed)} neighborhoods",
            "refreshed_count": len(refreshed),
            "refreshed_localities": refreshed,
            "errors": errors
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing neighborhoods: {str(e)}"
        )


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.core.database import get_db
from app.services.ml_service import MLService
from app.core.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from app.schemas.ml import CostPredictionRequest, CostPredictionResponse

router = APIRouter(prefix="/ml", tags=["machine-learning"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Get current user ID from token"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload.get("user_id")

ml_service = MLService()

@router.post("/predict-cost", response_model=CostPredictionResponse)
def predict_cost(
    request: CostPredictionRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Predict personalized monthly cost of living for a user in a locality
    
    user_profile should include:
    - income: float
    - family_size: int
    - property_type_preference: int (1=1BHK, 2=2BHK, 3=3BHK)
    - commute_days_per_week: int
    - distance_to_work_km: float
    - amenities_priority: int (1=low, 2=medium, 3=high)
    """
    try:
        prediction = ml_service.predict_cost(
            db=db,
            user_id=user_id,
            user_profile=request.user_profile,
            locality_id=request.locality_id
        )
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/classify-rent/{listing_id}")
def classify_rent_listing(
    listing_id: int,
    locality_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Classify a rent listing as 'fair' or 'overpriced'"""
    try:
        classification = ml_service.classify_rent_listing(
            db=db,
            listing_id=listing_id,
            locality_id=locality_id
        )
        return classification
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.get("/models/{model_name}/version")
def get_model_version(
    model_name: str,
    db: Session = Depends(get_db)
):
    """Get active model version information"""
    model_version = ml_service.get_active_model_version(db, model_name)
    if not model_version:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    return {
        'model_name': model_version.model_name,
        'version': model_version.version,
        'metrics': model_version.metrics,
        'created_at': model_version.created_at,
        'metadata': model_version.model_metadata
    }


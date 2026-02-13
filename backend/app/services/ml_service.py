from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from pathlib import Path
import logging
from app.models.ml_models import MLModelVersion, Prediction
from app.models.user import User

logger = logging.getLogger(__name__)

# Prefer local models dir when not in Docker
def _models_dir() -> Path:
    d = Path(__file__).resolve().parent.parent.parent / "models"
    docker_d = Path("/app/models")
    return docker_d if docker_d.exists() else d

class MLService:
    def __init__(self):
        self.models_dir = _models_dir()
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cost_predictor = None
        self.rent_classifier = None
        self._cost_predictor_loaded = False
        self._rent_classifier_loaded = False
        # Don't load models at startup - load lazily when needed
    
    def _load_cost_predictor(self):
        """Lazy load cost predictor model"""
        if self._cost_predictor_loaded:
            return
        try:
            from app.ml.cost_predictor import CostPredictor
            cost_model_path = self.models_dir / "cost_predictor" / "latest.pkl"
            if cost_model_path.exists():
                self.cost_predictor = CostPredictor(str(cost_model_path))
                logger.info("Cost predictor model loaded")
            else:
                # Initialize with default (untrained) model
                self.cost_predictor = CostPredictor()
                logger.warning("Cost predictor model not found, using default")
            self._cost_predictor_loaded = True
        except Exception as e:
            logger.error(f"Error loading cost predictor: {e}")
            self._cost_predictor_loaded = True  # Mark as attempted to avoid retry loops
    
    def _load_rent_classifier(self):
        """Lazy load rent classifier model"""
        if self._rent_classifier_loaded:
            return
        try:
            from app.ml.rent_classifier import RentClassifier
            rent_model_path = self.models_dir / "rent_classifier" / "latest"
            if rent_model_path.exists():
                self.rent_classifier = RentClassifier(str(rent_model_path))
                logger.info("Rent classifier model loaded")
            else:
                # Initialize with pretrained DistilBERT
                self.rent_classifier = RentClassifier()
                logger.info("Rent classifier initialized with pretrained model")
            self._rent_classifier_loaded = True
        except Exception as e:
            logger.error(f"Error loading rent classifier: {e}")
            self._rent_classifier_loaded = True  # Mark as attempted to avoid retry loops
    
    def predict_cost(
        self,
        db: Session,
        user_id: int,
        user_profile: Dict,
        locality_id: int
    ) -> Dict:
        """Predict cost of living for a user in a locality"""
        from app.services.geospatial_service import GeospatialService
        from app.services.rent_service import RentService
        from app.models.geospatial import Locality
        
        # Check if locality exists
        locality = db.query(Locality).filter(Locality.id == locality_id).first()
        if not locality:
            raise ValueError(f"Locality {locality_id} not found")
        
        # Get or create locality stats
        locality_stats = GeospatialService.get_locality_stats(db, locality_id)
        if not locality_stats:
            # Create stats if they don't exist
            locality_stats = GeospatialService.update_locality_stats(db, locality_id)
        
        # Prepare locality data - use property type from user profile
        property_type = user_profile.get('property_type_preference', 2)  # 1, 2, or 3
        rent_field_map = {
            1: 'avg_rent_1bhk',
            2: 'avg_rent_2bhk',
            3: 'avg_rent_3bhk'
        }
        rent_field = rent_field_map.get(property_type, 'avg_rent_2bhk')
        
        # Get rent based on property type preference
        rent_value = getattr(locality_stats, rent_field) or locality_stats.avg_rent_2bhk or 0
        
        # Prepare locality data with scraped data
        locality_data = {
            'avg_rent_2bhk': rent_value,  # Use the appropriate rent for property type
            'avg_grocery_cost_monthly': locality_stats.avg_grocery_cost_monthly or 0,
            'avg_transport_cost_monthly': locality_stats.avg_transport_cost_monthly or 0,
            'cost_burden_index': locality_stats.cost_burden_index or 0,
        }
        
        # Load model if needed
        self._load_cost_predictor()
        
        # Make prediction
        if not self.cost_predictor or not self.cost_predictor.model:
            # Return simple calculation if model not available
            rent = locality_data['avg_rent_2bhk']
            groceries = locality_data['avg_grocery_cost_monthly']
            transport = locality_data['avg_transport_cost_monthly']
            total = rent + groceries + transport
            
            prediction_result = {
                'predicted_monthly_cost': total,
                'breakdown': {
                    'rent': rent,
                    'groceries': groceries,
                    'transport': transport
                },
                'confidence': 0.5,
                'model_available': False
            }
        else:
            prediction_result = self.cost_predictor.predict(user_profile, locality_data)
            prediction_result['model_available'] = True
        
        # Convert all numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            """Recursively convert numpy types to native Python types"""
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_to_native(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj
        
        prediction_result = convert_to_native(prediction_result)
        
        # Save prediction to database
        prediction = Prediction(
            user_id=user_id,
            model_name='cost_predictor',
            input_data={'user_profile': user_profile, 'locality_id': locality_id},
            prediction=prediction_result,
            confidence=float(prediction_result.get('confidence', 0.5))
        )
        db.add(prediction)
        db.commit()
        
        return prediction_result
    
    def classify_rent_listing(
        self,
        db: Session,
        listing_id: int,
        locality_id: Optional[int] = None
    ) -> Dict:
        """Classify a rent listing as fair or overpriced"""
        from app.models.rent import RentListing
        from app.services.rent_service import RentService
        
        # Get listing
        listing = db.query(RentListing).filter(RentListing.id == listing_id).first()
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        
        # Get locality average rent if locality_id provided
        locality_avg_rent = None
        if locality_id:
            locality_avg_rent = RentService.get_avg_rent_by_locality(
                db, locality_id, listing.property_type
            )
        elif listing.locality_id:
            locality_avg_rent = RentService.get_avg_rent_by_locality(
                db, listing.locality_id, listing.property_type
            )
        
        # Prepare listing data
        listing_data = {
            'title': listing.title,
            'description': listing.description or '',
            'property_type': listing.property_type,
            'area_sqft': listing.area_sqft,
            'furnished': listing.furnished,
            'rent_amount': listing.rent_amount,
        }
        
        # Load model if needed
        self._load_rent_classifier()
        
        # Classify
        if not self.rent_classifier:
            # Simple rule-based classification if model not available
            if locality_avg_rent:
                diff_percent = ((listing.rent_amount - locality_avg_rent) / locality_avg_rent) * 100
                classification = 'overpriced' if diff_percent > 20 else 'fair'
                confidence = 0.6
            else:
                classification = 'fair'
                confidence = 0.5
            
            result = {
                'classification': classification,
                'confidence': confidence,
                'model_available': False
            }
        else:
            result = self.rent_classifier.classify(listing_data, locality_avg_rent)
            result['model_available'] = True
        
        return result
    
    def get_active_model_version(self, db: Session, model_name: str) -> Optional[MLModelVersion]:
        """Get the active version of a model"""
        return db.query(MLModelVersion).filter(
            MLModelVersion.model_name == model_name,
            MLModelVersion.is_active == True
        ).first()
    
    def save_model_version(
        self,
        db: Session,
        model_name: str,
        version: str,
        model_path: str,
        metrics: Dict,
        metadata: Optional[Dict] = None
    ) -> MLModelVersion:
        """Save a new model version"""
        # Deactivate old versions
        db.query(MLModelVersion).filter(
            MLModelVersion.model_name == model_name
        ).update({'is_active': False})
        
        # Create new version
        model_version = MLModelVersion(
            model_name=model_name,
            version=version,
            model_path=model_path,
            metrics=metrics,
            model_metadata=metadata or {},
            is_active=True
        )
        db.add(model_version)
        db.commit()
        db.refresh(model_version)
        
        return model_version


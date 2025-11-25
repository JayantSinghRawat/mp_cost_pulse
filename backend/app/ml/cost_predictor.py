"""
Cost of Living Prediction Model using XGBoost
Predicts personalized monthly cost of living based on user profile and locality
"""
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)

class CostPredictor:
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'locality_avg_rent_2bhk',
            'locality_avg_grocery_cost',
            'locality_avg_transport_cost',
            'locality_cost_burden_index',
            'user_income',
            'family_size',
            'preferred_property_type',  # 1=1BHK, 2=2BHK, 3=3BHK
            'commute_days_per_week',
            'distance_to_work_km',
            'amenities_priority',  # 1=low, 2=medium, 3=high
            # Additional features from public APIs
            'aqi_value',  # Air Quality Index
            'hospitals_count',  # Number of nearby hospitals
            'restaurants_count',  # Number of restaurants
            'avg_restaurant_rating',  # Average restaurant rating (cleanliness indicator)
            'schools_count',  # Number of schools
            'parks_count',  # Number of parks
        ]
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def prepare_features(self, user_profile: Dict, locality_stats: Dict) -> np.ndarray:
        """Prepare feature vector from user profile and locality stats"""
        features = np.array([
            locality_stats.get('avg_rent_2bhk', 0),
            locality_stats.get('avg_grocery_cost_monthly', 0),
            locality_stats.get('avg_transport_cost_monthly', 0),
            locality_stats.get('cost_burden_index', 0),
            user_profile.get('income', 0),
            user_profile.get('family_size', 1),
            user_profile.get('property_type_preference', 2),  # Default to 2BHK
            user_profile.get('commute_days_per_week', 5),
            user_profile.get('distance_to_work_km', 0),
            user_profile.get('amenities_priority', 2),
            # Additional features from public APIs (with defaults if not available)
            locality_stats.get('aqi_value', 50),
            locality_stats.get('hospitals_count', 0),
            locality_stats.get('restaurants_count', 0),
            locality_stats.get('avg_restaurant_rating', 3.5),
            locality_stats.get('schools_count', 0),
            locality_stats.get('parks_count', 0),
        ])
        return features.reshape(1, -1)
    
    def train(self, training_data: pd.DataFrame, target_column: str = 'total_monthly_cost'):
        """Train the cost prediction model"""
        logger.info("Training cost prediction model...")
        
        # Prepare features and target
        X = training_data[self.feature_names]
        y = training_data[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            objective='reg:squarederror'
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Model trained - Train R²: {train_score:.4f}, Test R²: {test_score:.4f}")
        
        # Convert feature importance to native Python types
        feature_importance = {
            name: float(val) for name, val in zip(self.feature_names, self.model.feature_importances_)
        }
        
        return {
            'train_r2': float(train_score),
            'test_r2': float(test_score),
            'feature_importance': feature_importance
        }
    
    def predict(self, user_profile: Dict, locality_stats: Dict) -> Dict:
        """Predict monthly cost of living"""
        if self.model is None:
            raise ValueError("Model not loaded or trained")
        
        features = self.prepare_features(user_profile, locality_stats)
        features_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(features_scaled)[0]
        
        # Get feature importance for explanation and convert numpy types to native Python types
        importance = {
            name: float(val) for name, val in zip(self.feature_names, self.model.feature_importances_)
        }
        
        return {
            'predicted_monthly_cost': float(prediction),
            'breakdown': {
                'rent': float(locality_stats.get('avg_rent_2bhk', 0)),
                'groceries': float(locality_stats.get('avg_grocery_cost_monthly', 0)),
                'transport': float(locality_stats.get('avg_transport_cost_monthly', 0)),
            },
            'feature_importance': importance,
            'confidence': 0.85  # Placeholder - could calculate from prediction variance
        }
    
    def save_model(self, model_path: str):
        """Save model and scaler"""
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load model and scaler"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data.get('feature_names', self.feature_names)
        logger.info(f"Model loaded from {model_path}")


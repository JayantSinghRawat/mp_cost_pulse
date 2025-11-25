#!/usr/bin/env python3
"""
Test script for the trained Cost Predictor Model
Tests predictions with sample MP data
"""
import sys
import os
sys.path.insert(0, '/app/backend')
sys.path.insert(0, '/app')

from app.ml.cost_predictor import CostPredictor
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model():
    """Test the trained model with sample MP data"""
    logger.info("Testing Cost Predictor Model...")
    
    # Load the trained model
    model_path = "/app/models/cost_predictor/latest.pkl"
    if not Path(model_path).exists():
        logger.error(f"Model not found at {model_path}")
        return
    
    logger.info(f"Loading model from {model_path}")
    model = CostPredictor(model_path=model_path)
    
    # Test cases for different MP cities
    test_cases = [
        {
            "name": "Bhopal - Arera Colony - 2BHK",
            "user_profile": {
                "income": 50000,
                "family_size": 3,
                "property_type_preference": 2,  # 2BHK
                "commute_days_per_week": 5,
                "distance_to_work_km": 10,
                "amenities_priority": 2,
            },
            "locality_stats": {
                "avg_rent_2bhk": 12000,
                "avg_grocery_cost_monthly": 4500,
                "avg_transport_cost_monthly": 2500,
                "cost_burden_index": 38.0,
            }
        },
        {
            "name": "Indore - Vijay Nagar - 2BHK",
            "user_profile": {
                "income": 75000,
                "family_size": 4,
                "property_type_preference": 2,
                "commute_days_per_week": 6,
                "distance_to_work_km": 15,
                "amenities_priority": 3,
            },
            "locality_stats": {
                "avg_rent_2bhk": 15000,
                "avg_grocery_cost_monthly": 5000,
                "avg_transport_cost_monthly": 3000,
                "cost_burden_index": 30.7,
            }
        },
        {
            "name": "Jabalpur - Civil Lines - 1BHK",
            "user_profile": {
                "income": 35000,
                "family_size": 2,
                "property_type_preference": 1,  # 1BHK
                "commute_days_per_week": 5,
                "distance_to_work_km": 8,
                "amenities_priority": 2,
            },
            "locality_stats": {
                "avg_rent_2bhk": 11500,  # Estimated from 1BHK
                "avg_grocery_cost_monthly": 4300,
                "avg_transport_cost_monthly": 2400,
                "cost_burden_index": 45.0,
            }
        },
        {
            "name": "Ujjain - Freeganj - 3BHK",
            "user_profile": {
                "income": 60000,
                "family_size": 5,
                "property_type_preference": 3,  # 3BHK
                "commute_days_per_week": 5,
                "distance_to_work_km": 12,
                "amenities_priority": 2,
            },
            "locality_stats": {
                "avg_rent_2bhk": 12000,  # Estimated from 3BHK
                "avg_grocery_cost_monthly": 4000,
                "avg_transport_cost_monthly": 2000,
                "cost_burden_index": 30.0,
            }
        },
    ]
    
    logger.info("\n" + "="*80)
    logger.info("TESTING MODEL PREDICTIONS")
    logger.info("="*80 + "\n")
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"Test Case {i}: {test_case['name']}")
        logger.info("-" * 80)
        
        try:
            prediction = model.predict(
                test_case["user_profile"],
                test_case["locality_stats"]
            )
            
            # Calculate expected cost manually for comparison
            expected_cost = (
                test_case["locality_stats"]["avg_rent_2bhk"] +
                test_case["locality_stats"]["avg_grocery_cost_monthly"] +
                test_case["locality_stats"]["avg_transport_cost_monthly"]
            )
            
            logger.info(f"User Profile:")
            logger.info(f"  Income: ₹{test_case['user_profile']['income']:,}/month")
            logger.info(f"  Family Size: {test_case['user_profile']['family_size']}")
            logger.info(f"  Property Type: {test_case['user_profile']['property_type_preference']}BHK")
            logger.info(f"  Commute Days/Week: {test_case['user_profile']['commute_days_per_week']}")
            
            logger.info(f"\nLocality Stats:")
            logger.info(f"  Avg Rent (2BHK): ₹{test_case['locality_stats']['avg_rent_2bhk']:,}/month")
            logger.info(f"  Avg Grocery Cost: ₹{test_case['locality_stats']['avg_grocery_cost_monthly']:,}/month")
            logger.info(f"  Avg Transport Cost: ₹{test_case['locality_stats']['avg_transport_cost_monthly']:,}/month")
            
            logger.info(f"\nPrediction Results:")
            logger.info(f"  Predicted Monthly Cost: ₹{prediction['predicted_monthly_cost']:,.2f}")
            logger.info(f"  Expected Base Cost: ₹{expected_cost:,.2f}")
            logger.info(f"  Confidence: {prediction['confidence']:.2%}")
            
            logger.info(f"\nCost Breakdown:")
            logger.info(f"  Rent: ₹{prediction['breakdown']['rent']:,.2f}")
            logger.info(f"  Groceries: ₹{prediction['breakdown']['groceries']:,.2f}")
            logger.info(f"  Transport: ₹{prediction['breakdown']['transport']:,.2f}")
            
            logger.info(f"\nTop Feature Importance:")
            sorted_features = sorted(
                prediction['feature_importance'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            for feature, importance in sorted_features:
                logger.info(f"  {feature}: {importance:.4f}")
            
            results.append({
                "test_case": test_case["name"],
                "predicted_cost": prediction['predicted_monthly_cost'],
                "expected_cost": expected_cost,
                "confidence": prediction['confidence'],
                "success": True
            })
            
        except Exception as e:
            logger.error(f"Error in test case {i}: {e}")
            results.append({
                "test_case": test_case["name"],
                "success": False,
                "error": str(e)
            })
        
        logger.info("\n" + "="*80 + "\n")
    
    # Summary
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    successful = sum(1 for r in results if r.get("success", False))
    logger.info(f"Successful tests: {successful}/{len(test_cases)}")
    
    if successful > 0:
        avg_predicted = sum(r["predicted_cost"] for r in results if r.get("success"))
        avg_expected = sum(r["expected_cost"] for r in results if r.get("success"))
        logger.info(f"Average Predicted Cost: ₹{avg_predicted/successful:,.2f}")
        logger.info(f"Average Expected Cost: ₹{avg_expected/successful:,.2f}")
        logger.info(f"Average Difference: ₹{abs(avg_predicted - avg_expected)/successful:,.2f}")
    
    logger.info("\n✅ Model testing completed!")
    
    return results

if __name__ == "__main__":
    test_model()


#!/bin/bash

# Test Cost Prediction API
# Note: This requires authentication token

echo "=========================================="
echo "Testing Cost Prediction API"
echo "=========================================="
echo ""
echo "To test the Cost Prediction feature:"
echo ""
echo "1. Open http://localhost in your browser"
echo "2. Log in if not already logged in"
echo "3. Go to 'Cost Prediction' page"
echo "4. Fill in the form:"
echo "   - Monthly Income: 50000"
echo "   - Family Size: 2"
echo "   - Property Type: 2 BHK"
echo "   - Commute Days/Week: 5"
echo "   - Distance to Work: 10 km"
echo "   - Amenities Priority: Medium"
echo "   - Select a locality from dropdown"
echo "5. Click 'Get Cost Prediction'"
echo ""
echo "Expected Result:"
echo "  - Prediction results should appear"
echo "  - Shows predicted monthly cost"
echo "  - Shows breakdown: Rent, Groceries, Transport"
echo "  - Shows confidence level"
echo ""
echo "=========================================="
echo "API Endpoint:"
echo "=========================================="
echo "POST /api/v1/ml/predict-cost"
echo ""
echo "Request Body:"
echo '{'
echo '  "user_profile": {'
echo '    "income": 50000,'
echo '    "family_size": 2,'
echo '    "property_type_preference": 2,'
echo '    "commute_days_per_week": 5,'
echo '    "distance_to_work_km": 10,'
echo '    "amenities_priority": 2'
echo '  },'
echo '  "locality_id": 1'
echo '}'
echo ""
echo "Note: Requires Bearer token in Authorization header"
echo ""


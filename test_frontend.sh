#!/bin/bash

# Quick Frontend Test Script
# Opens browser and provides testing instructions

echo "=========================================="
echo "Frontend Testing Guide"
echo "=========================================="
echo ""
echo "1. Open your browser and go to:"
echo "   http://localhost"
echo ""
echo "2. Navigate to 'Find Neighborhood' page"
echo ""
echo "3. Test each city:"
echo "   - Select city from dropdown"
echo "   - Set budget: ₹30,000"
echo "   - Click 'Get Recommendations'"
echo "   - Verify recommendations appear"
echo ""
echo "4. Check Food & Grocery Data:"
echo "   - Look for 'Food & Beverages' section"
echo "   - Verify restaurant count is shown"
echo "   - Check grocery cost is displayed"
echo "   - Verify grocery stores count"
echo ""
echo "5. Test Different Cities:"
echo "   - Bhopal"
echo "   - Indore"
echo "   - Gwalior"
echo "   - Jabalpur"
echo "   - Ujjain"
echo ""
echo "=========================================="
echo "Quick API Test (run in another terminal):"
echo "=========================================="
echo ""
echo "Test Indore recommendations:"
echo 'curl -X POST "http://localhost:8000/api/v1/recommendations/neighborhoods" \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{"city": "Indore", "number_of_people": 2, "max_travel_distance_km": 5, "budget": 30000, "property_type": "2BHK", "top_n": 5}'"'"' \'
echo '  | python3 -m json.tool'
echo ""


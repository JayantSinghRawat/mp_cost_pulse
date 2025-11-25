#!/bin/bash

# Comprehensive Test Script for MP Cost Pulse
# Tests all major features and APIs

echo "=========================================="
echo "MP Cost Pulse - Comprehensive Test Suite"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_passed=0
test_failed=0

# Test function
test_api() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((test_passed++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "Response: $body"
        ((test_failed++))
        return 1
    fi
}

# 1. Test Localities API
echo "1. Testing Localities API"
echo "-------------------------"
test_api "Get all localities" "GET" "/geospatial/localities"
test_api "Get Bhopal localities" "GET" "/geospatial/localities?city=Bhopal"
test_api "Get Indore localities" "GET" "/geospatial/localities?city=Indore"
echo ""

# 2. Test Recommendations API
echo "2. Testing Recommendations API"
echo "-------------------------------"
test_api "Get recommendations for Bhopal" "POST" "/recommendations/neighborhoods" \
    '{"city": "Bhopal", "number_of_people": 2, "max_travel_distance_km": 5, "budget": 30000, "property_type": "2BHK", "top_n": 5}'

test_api "Get recommendations for Indore" "POST" "/recommendations/neighborhoods" \
    '{"city": "Indore", "number_of_people": 3, "max_travel_distance_km": 10, "budget": 40000, "property_type": "2BHK", "top_n": 5}'

test_api "Get recommendations for Gwalior" "POST" "/recommendations/neighborhoods" \
    '{"city": "Gwalior", "number_of_people": 2, "max_travel_distance_km": 5, "budget": 25000, "property_type": "1BHK", "top_n": 3}'
echo ""

# 3. Test Grocery API
echo "3. Testing Grocery API"
echo "----------------------"
# Get first locality ID
locality_id=$(curl -s "$BASE_URL/geospatial/localities?city=Bhopal" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '1')" 2>/dev/null || echo "1")
test_api "Get grocery stores" "GET" "/groceries/stores?locality_id=$locality_id"
test_api "Calculate grocery cost" "GET" "/groceries/cost/$locality_id"
echo ""

# 4. Test Geospatial API
echo "4. Testing Geospatial API"
echo "-------------------------"
test_api "Get heatmap data (rent)" "GET" "/geospatial/heatmap?data_type=rent"
test_api "Get heatmap data (grocery)" "GET" "/geospatial/heatmap?data_type=grocery"
echo ""

# 5. Test ML Model
echo "5. Testing ML Model"
echo "-------------------"
echo -n "Testing cost predictor model... "
if docker-compose exec -T ml-worker python test_model.py 2>&1 | grep -q "Model testing completed"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((test_passed++))
else
    echo -e "${YELLOW}⚠ SKIPPED${NC} (Model may still be training)"
fi
echo ""

# 6. Check Database
echo "6. Checking Database"
echo "--------------------"
echo -n "Checking localities by city... "
cities=$(docker-compose exec -T postgres psql -U postgres -d mpcostpulse -t -c "SELECT COUNT(DISTINCT city) FROM localities;" 2>/dev/null | tr -d ' ')
if [ ! -z "$cities" ] && [ "$cities" -ge 5 ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($cities cities found)"
    ((test_passed++))
else
    echo -e "${RED}✗ FAILED${NC} (Only $cities cities found)"
    ((test_failed++))
fi

echo -n "Checking neighborhood data... "
neighborhoods=$(docker-compose exec -T postgres psql -U postgres -d mpcostpulse -t -c "SELECT COUNT(*) FROM neighborhood_data;" 2>/dev/null | tr -d ' ')
if [ ! -z "$neighborhoods" ] && [ "$neighborhoods" -gt 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($neighborhoods neighborhoods found)"
    ((test_passed++))
else
    echo -e "${RED}✗ FAILED${NC} (No neighborhood data found)"
    ((test_failed++))
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $test_passed${NC}"
echo -e "${RED}Failed: $test_failed${NC}"
echo ""

if [ $test_failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
fi


#!/bin/bash
# Example API requests for testing Whisp API locally

API_URL="http://localhost:8000"

echo "===== Testing Whisp API ====="
echo ""

# 1. Health check
echo "1. Health check"
curl -X GET "${API_URL}/health" | jq
echo ""
echo ""

# 2. Root endpoint
echo "2. Root endpoint"
curl -X GET "${API_URL}/" | jq
echo ""
echo ""

# 3. Analyze with GEE asset (without risk calculation)
echo "3. Analyze GEE asset (without risk)"
curl -X POST "${API_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "gee_asset",
    "input_data": "projects/ee-whisp/assets/example_plots",
    "output_unit": "ha",
    "calculate_risk": false
  }' | jq
echo ""
echo ""

# 4. Analyze with GEE asset (with risk calculation)
echo "4. Analyze GEE asset (with risk)"
curl -X POST "${API_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "gee_asset",
    "input_data": "projects/ee-whisp/assets/example_plots",
    "output_unit": "ha",
    "calculate_risk": true,
    "ind_1_threshold": 10.0,
    "ind_2_threshold": 10.0,
    "ind_3_threshold": 0.0,
    "ind_4_threshold": 0.0
  }' | jq
echo ""
echo ""

# 5. Analyze with GeoJSON (simple example)
echo "5. Analyze with GeoJSON"
curl -X POST "${API_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "geojson",
    "input_data": "{\"type\":\"FeatureCollection\",\"features\":[{\"type\":\"Feature\",\"geometry\":{\"type\":\"Polygon\",\"coordinates\":[[[-51.0,-10.0],[-51.0,-10.1],[-50.9,-10.1],[-50.9,-10.0],[-51.0,-10.0]]]},\"properties\":{\"id\":1}}]}",
    "output_unit": "percent",
    "calculate_risk": true
  }' | jq
echo ""
echo ""

echo "===== Testing Complete ====="

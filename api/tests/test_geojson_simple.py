"""
Simple test script - GeoJSON without risk calculation
"""
import requests
import json

# Example GeoJSON - small polygon in Brazil
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"id": 1, "name": "Test Plot"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-60.0, -3.0],
                    [-60.0, -3.05],
                    [-59.95, -3.05],
                    [-59.95, -3.0],
                    [-60.0, -3.0]
                ]]
            }
        }
    ]
}

payload = {
    "input_type": "geojson",
    "input_data": json.dumps(geojson),
    "output_unit": "ha",
    "calculate_risk": False  # Test without risk first
}

print("Testing Whisp API with GeoJSON (no risk calculation)...")
print("=" * 70)

response = requests.post("http://localhost:9005/analyze", json=payload, timeout=120)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print("\n✓ SUCCESS!")
    print(f"Status: {result['status']}")
    print(f"Features: {result['num_features']}")
    print(f"\nFirst Plot Data:")
    if result['results']:
        plot = result['results'][0]
        print(json.dumps(plot, indent=2))
else:
    print("\n✗ ERROR:")
    print(json.dumps(response.json(), indent=2))

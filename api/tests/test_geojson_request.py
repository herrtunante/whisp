"""
Test script to send a GeoJSON to the Whisp API
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:9005/analyze"

# Example GeoJSON - a small polygon in Brazil (Amazon region)
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": 1,
                "name": "Test Plot 1"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-60.0, -3.0],
                        [-60.0, -3.05],
                        [-59.95, -3.05],
                        [-59.95, -3.0],
                        [-60.0, -3.0]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": 2,
                "name": "Test Plot 2"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-51.0, -10.0],
                        [-51.0, -10.05],
                        [-50.95, -10.05],
                        [-50.95, -10.0],
                        [-51.0, -10.0]
                    ]
                ]
            }
        }
    ]
}

# Convert GeoJSON to string
geojson_str = json.dumps(geojson)

# Prepare request payload
payload = {
    "input_type": "geojson",
    "input_data": geojson_str,
    "output_unit": "ha",
    "calculate_risk": True,
    "ind_1_threshold": 10.0,
    "ind_2_threshold": 10.0,
    "ind_3_threshold": 0.0,
    "ind_4_threshold": 0.0
}

print("=" * 70)
print("Testing Whisp API with GeoJSON")
print("=" * 70)
print(f"\nAPI URL: {API_URL}")
print(f"Number of features: {len(geojson['features'])}")
print(f"Output unit: {payload['output_unit']}")
print(f"Calculate risk: {payload['calculate_risk']}")
print("\nSending request...")
print("-" * 70)

try:
    # Send POST request
    response = requests.post(API_URL, json=payload, timeout=120)

    # Check response status
    print(f"\nResponse Status Code: {response.status_code}")

    if response.status_code == 200:
        print("✓ Success!")

        # Parse response
        result = response.json()

        print("\nResponse Summary:")
        print("-" * 70)
        print(f"Status: {result['status']}")
        print(f"Number of features analyzed: {result['num_features']}")
        print(f"Output unit: {result['output_unit']}")
        print(f"Risk calculated: {result['risk_calculated']}")
        print(f"Message: {result.get('message', 'N/A')}")

        # Display results for each plot
        if result.get('results'):
            print("\nPlot Results:")
            print("=" * 70)
            for i, plot in enumerate(result['results'], 1):
                print(f"\nPlot {i}:")
                print(f"  ID: {plot.get('Plot_ID', 'N/A')}")
                print(f"  Area: {plot.get('Plot_area_ha', 'N/A')} ha")
                print(f"  Country: {plot.get('Country', 'N/A')}")
                print(f"  Admin Level 1: {plot.get('Admin_Level_1', 'N/A')}")
                print(f"  Centroid: ({plot.get('Centroid_lon', 'N/A')}, {plot.get('Centroid_lat', 'N/A')})")
                print(f"  In Waterbody: {plot.get('In_waterbody', 'N/A')}")

                if result['risk_calculated']:
                    print(f"\n  Risk Indicators:")
                    print(f"    Indicator 1 (Treecover): {plot.get('Indicator_1_treecover', 'N/A')}")
                    print(f"    Indicator 2 (Commodities): {plot.get('Indicator_2_commodities', 'N/A')}")
                    print(f"    Indicator 3 (Disturbance before 2020): {plot.get('Indicator_3_disturbance_before_2020', 'N/A')}")
                    print(f"    Indicator 4 (Disturbance after 2020): {plot.get('Indicator_4_disturbance_after_2020', 'N/A')}")
                    print(f"    EUDR Risk: {plot.get('EUDR_risk', 'N/A')}")

                # Show a few dataset statistics
                print(f"\n  Sample Statistics:")
                dataset_count = 0
                for key, value in plot.items():
                    if key not in ['Plot_ID', 'Plot_area_ha', 'Geometry_type', 'Country',
                                   'Admin_Level_1', 'Centroid_lon', 'Centroid_lat',
                                   'In_waterbody', 'Unit', 'Indicator_1_treecover',
                                   'Indicator_2_commodities', 'Indicator_3_disturbance_before_2020',
                                   'Indicator_4_disturbance_after_2020', 'EUDR_risk']:
                        if dataset_count < 5:  # Show first 5 datasets
                            print(f"    {key}: {value}")
                            dataset_count += 1

                if dataset_count < len(plot) - 14:
                    print(f"    ... and {len(plot) - dataset_count - 14} more datasets")

        # Save full response to file
        output_file = "/mnt/c/Users/Alfonso Sanchez-Paus/git/whisp/api/tests/test_response.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Full response saved to: {output_file}")

    else:
        print("✗ Error!")
        print("\nError Details:")
        print("-" * 70)
        try:
            error = response.json()
            print(json.dumps(error, indent=2))
        except:
            print(response.text)

except requests.exceptions.Timeout:
    print("\n✗ Request timed out!")
    print("The analysis may take longer for large datasets.")

except requests.exceptions.ConnectionError:
    print("\n✗ Connection error!")
    print("Make sure the API server is running at http://localhost:9005")

except Exception as e:
    print(f"\n✗ Unexpected error: {e}")

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)

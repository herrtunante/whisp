#!/usr/bin/env python3
"""
Test script to compare local API results with production API results.
Tests using the geojson_example.geojson file.
"""

import json
import requests
import time
from pathlib import Path

# Configuration
LOCAL_API_URL = "http://localhost:9006/analyze"
PROD_API_URL = "https://whisp.openforis.org/api/submit/geojson"
PROD_API_KEY = "c3fa0a20-ca9a-48f4-ae4a-b255c913776f"
GEOJSON_PATH = Path("/mnt/c/Users/Alfonso Sanchez-Paus/git/whisp/input_examples/geojson_example.geojson")

def load_geojson():
    """Load the test GeoJSON file."""
    with open(GEOJSON_PATH, 'r') as f:
        return json.load(f)

def test_local_api(geojson_data):
    """Test the local API."""
    print("=" * 80)
    print("TESTING LOCAL API")
    print("=" * 80)
    print(f"Endpoint: {LOCAL_API_URL}")
    print(f"Features: {len(geojson_data['features'])}")
    print()

    start_time = time.time()

    try:
        response = requests.post(
            LOCAL_API_URL,
            json={
                "input_type": "geojson",
                "input_data": json.dumps(geojson_data),
                "output_unit": "ha",
                "calculate_risk": True,
                "ind_1_threshold": 10.0,
                "ind_2_threshold": 10.0,
                "ind_3_threshold": 0.0,
                "ind_4_threshold": 0.0
            },
            timeout=300
        )

        elapsed = time.time() - start_time

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f} seconds")

        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result.get('status', 'N/A')}")
            print(f"Features returned: {len(result.get('results', []))}")

            # Show first feature properties (sample)
            if result.get('results'):
                first_result = result['results'][0]
                print(f"\nFirst feature properties (sample):")
                print(f"  - Keys count: {len(first_result)}")
                print(f"  - Has 'EUDR_risk'?: {'EUDR_risk' in first_result}")
                print(f"  - EUDR risk value: {first_result.get('EUDR_risk', 'N/A')}")

                # Show a few dataset values as sample
                sample_keys = [k for k in list(first_result.keys())[:5] if k not in ['FID', 'id', 'EUDR_risk']]
                if sample_keys:
                    print(f"  - Sample datasets:")
                    for key in sample_keys:
                        print(f"    {key}: {first_result.get(key)}")

            return result
        else:
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def test_production_api(geojson_data):
    """Test the production API."""
    print("\n" + "=" * 80)
    print("TESTING PRODUCTION API")
    print("=" * 80)
    print(f"Endpoint: {PROD_API_URL}")
    print(f"Features: {len(geojson_data['features'])}")
    print()

    start_time = time.time()

    try:
        # Production API expects GeoJSON with calculate_risk parameter
        payload = {
            "geojson": geojson_data,
            "calculate_risk": True,
            "ind_1_threshold": 10.0,
            "ind_2_threshold": 10.0,
            "ind_3_threshold": 0.0,
            "ind_4_threshold": 0.0
        }

        response = requests.post(
            PROD_API_URL,
            json=payload,
            headers={
                "X-API-Key": PROD_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=300
        )

        elapsed = time.time() - start_time

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f} seconds")

        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")

            # Production API returns data differently - check structure
            data = result.get('data', result)

            # Handle both possible response structures
            if isinstance(data, dict) and 'features' in data:
                features = data['features']
            elif isinstance(data, list):
                features = data
            else:
                features = []

            print(f"Features returned: {len(features)}")

            # Show first feature properties (sample)
            if features:
                first_feature = features[0]
                props = first_feature.get('properties', first_feature)
                print(f"\nFirst feature properties (sample):")
                print(f"  - Keys count: {len(props)}")
                print(f"  - Has 'eudr_risk'?: {'eudr_risk' in props}")
                print(f"  - EUDR risk value: {props.get('eudr_risk', 'N/A')}")

                # Show a few dataset values as sample
                sample_keys = [k for k in list(props.keys())[:5] if k not in ['FID', 'id', 'eudr_risk']]
                if sample_keys:
                    print(f"  - Sample datasets:")
                    for key in sample_keys:
                        print(f"    {key}: {props.get(key)}")

            return result
        else:
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def compare_results(local_result, prod_result):
    """Compare results from local and production APIs."""
    print("\n" + "=" * 80)
    print("COMPARISON")
    print("=" * 80)

    if not local_result or not prod_result:
        print("Cannot compare - one or both API calls failed")
        return

    # Extract features - local API returns results directly
    local_features = local_result.get('results', [])

    prod_data = prod_result.get('data', prod_result)
    if isinstance(prod_data, dict) and 'features' in prod_data:
        prod_features = prod_data['features']
    elif isinstance(prod_data, list):
        prod_features = prod_data
    else:
        prod_features = []

    print(f"\nFeature count:")
    print(f"  Local:      {len(local_features)}")
    print(f"  Production: {len(prod_features)}")
    print(f"  Match: {'✓' if len(local_features) == len(prod_features) else '✗'}")

    if not local_features or not prod_features:
        print("\nNo features to compare")
        return

    # Compare first feature properties - local returns properties directly in results
    local_props = local_features[0]
    prod_props = prod_features[0].get('properties', prod_features[0])

    print(f"\nFirst feature property count:")
    print(f"  Local:      {len(local_props)} keys")
    print(f"  Production: {len(prod_props)} keys")

    # Find common and different keys
    local_keys = set(local_props.keys())
    prod_keys = set(prod_props.keys())

    common_keys = local_keys & prod_keys
    only_local = local_keys - prod_keys
    only_prod = prod_keys - local_keys

    print(f"\nKey comparison:")
    print(f"  Common keys: {len(common_keys)}")
    print(f"  Only in local: {len(only_local)}")
    if only_local and len(only_local) <= 10:
        print(f"    {', '.join(sorted(only_local))}")
    print(f"  Only in production: {len(only_prod)}")
    if only_prod and len(only_prod) <= 10:
        print(f"    {', '.join(sorted(only_prod))}")

    # Compare EUDR risk values for first few features
    print(f"\nEUDR Risk comparison (first 5 features):")
    for i in range(min(5, len(local_features), len(prod_features))):
        local_risk = local_features[i].get('EUDR_risk', 'N/A')
        prod_risk = prod_features[i].get('properties', prod_features[i]).get('eudr_risk', 'N/A')
        match = '✓' if str(local_risk).lower() == str(prod_risk).lower() else '✗'
        print(f"  Feature {i}: Local={str(local_risk):20s} Prod={str(prod_risk):20s} {match}")

    # Compare a few dataset values for first feature
    print(f"\nSample dataset values (first feature):")
    sample_keys = [k for k in sorted(common_keys)[:10] if k not in ['FID', 'id', 'eudr_risk', 'Country', 'Admin_0', 'Admin_1', 'Admin_2']]

    if sample_keys:
        for key in sample_keys:
            local_val = local_props.get(key, 'N/A')
            prod_val = prod_props.get(key, 'N/A')

            # Compare with tolerance for floating point
            if isinstance(local_val, (int, float)) and isinstance(prod_val, (int, float)):
                match = '✓' if abs(local_val - prod_val) < 0.01 else '✗'
            else:
                match = '✓' if local_val == prod_val else '✗'

            print(f"  {key:30s}: Local={str(local_val):15s} Prod={str(prod_val):15s} {match}")

def main():
    """Main test function."""
    print("=" * 80)
    print("WHISP API COMPARISON TEST")
    print("=" * 80)
    print(f"GeoJSON file: {GEOJSON_PATH}")
    print()

    # Load GeoJSON
    geojson_data = load_geojson()
    print(f"Loaded GeoJSON with {len(geojson_data['features'])} features")
    print()

    # Test local API
    local_result = test_local_api(geojson_data)

    # Test production API
    prod_result = test_production_api(geojson_data)

    # Compare results
    compare_results(local_result, prod_result)

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

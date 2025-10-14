#!/usr/bin/env python3
"""
Test script to compare local API results with production API results.
Tests using the geojson_example.geojson file and generates an Excel comparison report.
"""

import json
import requests
import time
from pathlib import Path
import pandas as pd
from datetime import datetime

# Configuration
LOCAL_API_URL = "http://localhost:9006/analyze"
PROD_API_URL = "https://whisp.openforis.org/api/submit/geojson"
PROD_API_KEY = "c3fa0a20-ca9a-48f4-ae4a-b255c913776f"
GEOJSON_PATH = Path("/mnt/c/Users/Alfonso Sanchez-Paus/git/whisp/input_examples/geojson_example.geojson")
OUTPUT_PATH = Path("/mnt/c/Users/Alfonso Sanchez-Paus/git/whisp/api/tests/api_comparison_results.xlsx")

def load_geojson():
    """Load the test GeoJSON file."""
    with open(GEOJSON_PATH, 'r') as f:
        return json.load(f)

def test_local_api(geojson_data):
    """Test the local API."""
    print("Testing Local API...")

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

        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Success - {len(result.get('results', []))} features in {elapsed:.2f}s")
            return result, elapsed
        else:
            print(f"  ✗ Error {response.status_code}: {response.text}")
            return None, elapsed

    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")
        return None, 0

def test_production_api(geojson_data):
    """Test the production API."""
    print("Testing Production API...")

    start_time = time.time()

    try:
        # Production API expects GeoJSON directly, with query parameters for options
        response = requests.post(
            PROD_API_URL,
            json=geojson_data,
            params={
                "calculate_risk": "true",
                "ind_1_threshold": 10.0,
                "ind_2_threshold": 10.0,
                "ind_3_threshold": 0.0,
                "ind_4_threshold": 0.0
            },
            headers={
                "X-API-Key": PROD_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=300
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            # Extract features from response
            data = result.get('data', result)
            if isinstance(data, dict) and 'features' in data:
                features = data['features']
            elif isinstance(data, list):
                features = data
            else:
                features = []

            print(f"  ✓ Success - {len(features)} features in {elapsed:.2f}s")
            return result, elapsed, features
        else:
            print(f"  ✗ Error {response.status_code}: {response.text}")
            return None, elapsed, []

    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")
        return None, 0, []

def create_comparison_excel(local_result, local_time, prod_result, prod_time, prod_features):
    """Create comprehensive Excel comparison report."""

    print("\nGenerating Excel comparison report...")

    # Extract data
    local_features = local_result.get('results', []) if local_result else []

    # Create Excel writer
    with pd.ExcelWriter(OUTPUT_PATH, engine='openpyxl') as writer:

        # Sheet 1: Summary
        summary_data = {
            'Metric': [
                'Test Date/Time',
                'Number of Features',
                'Local Response Time (s)',
                'Production Response Time (s)',
                'Local Status',
                'Production Status',
                'Local Properties Count',
                'Production Properties Count',
                'Common Properties',
                'Only in Local',
                'Only in Production'
            ],
            'Value': [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                len(local_features),
                f"{local_time:.2f}",
                f"{prod_time:.2f}",
                local_result.get('status', 'N/A') if local_result else 'Failed',
                'Success' if prod_features else 'Failed',
                len(local_features[0]) if local_features else 0,
                len(prod_features[0].get('properties', {})) if prod_features else 0,
                '', '', ''  # Will be filled in below
            ]
        }

        if local_features and prod_features:
            local_keys = set(local_features[0].keys())
            prod_keys = set(prod_features[0].get('properties', {}).keys())
            common = local_keys & prod_keys
            only_local = local_keys - prod_keys
            only_prod = prod_keys - local_keys

            summary_data['Value'][8] = len(common)
            summary_data['Value'][9] = len(only_local)
            summary_data['Value'][10] = len(only_prod)

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Sheet 2: Local Results (all features, all properties)
        if local_features:
            local_df = pd.DataFrame(local_features)
            local_df.to_excel(writer, sheet_name='Local Results', index=False)
            print(f"  ✓ Local Results: {len(local_df)} rows, {len(local_df.columns)} columns")

        # Sheet 3: Production Results (all features, all properties)
        if prod_features:
            # Extract properties from features
            prod_props = [f.get('properties', f) for f in prod_features]
            prod_df = pd.DataFrame(prod_props)
            prod_df.to_excel(writer, sheet_name='Production Results', index=False)
            print(f"  ✓ Production Results: {len(prod_df)} rows, {len(prod_df.columns)} columns")

        # Sheet 4: Side-by-Side Comparison (first feature only for readability)
        if local_features and prod_features:
            local_props = local_features[0]
            prod_props = prod_features[0].get('properties', prod_features[0])

            # Get all unique keys
            all_keys = sorted(set(list(local_props.keys()) + list(prod_props.keys())))

            comparison_data = []
            for key in all_keys:
                local_val = local_props.get(key, 'N/A')
                prod_val = prod_props.get(key, 'N/A')

                # Determine if values match
                if local_val == 'N/A' or prod_val == 'N/A':
                    match = 'Missing'
                    diff = ''
                elif isinstance(local_val, (int, float)) and isinstance(prod_val, (int, float)):
                    match = 'Match' if abs(float(local_val) - float(prod_val)) < 0.01 else 'Different'
                    diff = abs(float(local_val) - float(prod_val)) if match == 'Different' else 0
                else:
                    match = 'Match' if str(local_val).lower() == str(prod_val).lower() else 'Different'
                    diff = ''

                comparison_data.append({
                    'Property': key,
                    'Local Value': local_val,
                    'Production Value': prod_val,
                    'Match': match,
                    'Difference': diff
                })

            comparison_df = pd.DataFrame(comparison_data)
            comparison_df.to_excel(writer, sheet_name='First Feature Comparison', index=False)
            print(f"  ✓ First Feature Comparison: {len(comparison_df)} properties")

        # Sheet 5: EUDR Risk Comparison (all features)
        if local_features and prod_features:
            risk_data = []
            for i in range(min(len(local_features), len(prod_features))):
                local_risk = local_features[i].get('EUDR_risk', 'N/A')
                prod_props = prod_features[i].get('properties', prod_features[i])
                prod_risk = prod_props.get('eudr_risk', prod_props.get('EUDR_risk', 'N/A'))

                match = 'Match' if str(local_risk).lower() == str(prod_risk).lower() else 'Different'

                risk_data.append({
                    'Feature Index': i,
                    'Local EUDR Risk': local_risk,
                    'Production EUDR Risk': prod_risk,
                    'Match': match,
                    'Local Ind 1': local_features[i].get('Indicator_1_treecover', 'N/A'),
                    'Prod Ind 1': prod_props.get('indicator_1_treecover', prod_props.get('Indicator_1_treecover', 'N/A')),
                    'Local Ind 2': local_features[i].get('Indicator_2_commodities', 'N/A'),
                    'Prod Ind 2': prod_props.get('indicator_2_commodities', prod_props.get('Indicator_2_commodities', 'N/A')),
                    'Local Ind 3': local_features[i].get('Indicator_3_disturbance_before_2020', 'N/A'),
                    'Prod Ind 3': prod_props.get('indicator_3_disturbance_before_2020', prod_props.get('Indicator_3_disturbance_before_2020', 'N/A')),
                    'Local Ind 4': local_features[i].get('Indicator_4_disturbance_after_2020', 'N/A'),
                    'Prod Ind 4': prod_props.get('indicator_4_disturbance_after_2020', prod_props.get('Indicator_4_disturbance_after_2020', 'N/A'))
                })

            risk_df = pd.DataFrame(risk_data)
            risk_df.to_excel(writer, sheet_name='EUDR Risk Comparison', index=False)
            print(f"  ✓ EUDR Risk Comparison: {len(risk_df)} features")

        # Sheet 6: Property Differences
        if local_features and prod_features:
            local_keys = set(local_features[0].keys())
            prod_keys = set(prod_features[0].get('properties', {}).keys())

            diff_data = []

            # Properties only in local
            only_local = local_keys - prod_keys
            for key in sorted(only_local):
                diff_data.append({
                    'Property': key,
                    'Location': 'Only in Local',
                    'Sample Value': str(local_features[0].get(key, ''))[:100]
                })

            # Properties only in production
            only_prod = prod_keys - local_keys
            for key in sorted(only_prod):
                diff_data.append({
                    'Property': key,
                    'Location': 'Only in Production',
                    'Sample Value': str(prod_features[0].get('properties', {}).get(key, ''))[:100]
                })

            if diff_data:
                diff_df = pd.DataFrame(diff_data)
                diff_df.to_excel(writer, sheet_name='Property Differences', index=False)
                print(f"  ✓ Property Differences: {len(diff_df)} differences")

        # Sheet 7: Value Differences (properties with different values)
        if local_features and prod_features:
            value_diff_data = []

            local_props = local_features[0]
            prod_props = prod_features[0].get('properties', prod_features[0])
            common_keys = set(local_props.keys()) & set(prod_props.keys())

            for key in sorted(common_keys):
                local_val = local_props.get(key)
                prod_val = prod_props.get(key)

                # Check if values are different
                if isinstance(local_val, (int, float)) and isinstance(prod_val, (int, float)):
                    if abs(float(local_val) - float(prod_val)) >= 0.01:
                        value_diff_data.append({
                            'Property': key,
                            'Local Value': local_val,
                            'Production Value': prod_val,
                            'Absolute Difference': abs(float(local_val) - float(prod_val)),
                            'Relative Difference %': abs(float(local_val) - float(prod_val)) / max(abs(float(local_val)), 0.0001) * 100 if local_val != 0 else 'N/A'
                        })
                elif str(local_val) != str(prod_val):
                    value_diff_data.append({
                        'Property': key,
                        'Local Value': str(local_val)[:100],
                        'Production Value': str(prod_val)[:100],
                        'Absolute Difference': 'N/A (text)',
                        'Relative Difference %': 'N/A'
                    })

            if value_diff_data:
                value_diff_df = pd.DataFrame(value_diff_data)
                value_diff_df.to_excel(writer, sheet_name='Value Differences', index=False)
                print(f"  ✓ Value Differences: {len(value_diff_df)} properties with different values")

    print(f"\n✓ Excel file saved: {OUTPUT_PATH}")

def main():
    """Main test function."""
    print("=" * 80)
    print("WHISP API COMPARISON TEST WITH EXCEL EXPORT")
    print("=" * 80)
    print(f"GeoJSON file: {GEOJSON_PATH}")
    print(f"Output file: {OUTPUT_PATH}")
    print()

    # Load GeoJSON
    geojson_data = load_geojson()
    print(f"Loaded GeoJSON with {len(geojson_data['features'])} features\n")

    # Test local API
    local_result, local_time = test_local_api(geojson_data)

    # Test production API
    prod_result, prod_time, prod_features = test_production_api(geojson_data)

    # Generate Excel comparison
    if local_result or prod_result:
        create_comparison_excel(local_result, local_time, prod_result, prod_time, prod_features)
    else:
        print("\n✗ Both API calls failed - cannot generate comparison")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

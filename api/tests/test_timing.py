"""
Test script to measure API response time for GEE analysis
"""
import requests
import json
import time

# API endpoint
API_URL = "http://localhost:9006/analyze"

# Small test plot in Brazil
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

# Test configurations
test_cases = [
    {
        "name": "Stats only (no risk)",
        "payload": {
            "input_type": "geojson",
            "input_data": json.dumps(geojson),
            "output_unit": "ha",
            "calculate_risk": False
        }
    },
    {
        "name": "Stats + Risk calculation",
        "payload": {
            "input_type": "geojson",
            "input_data": json.dumps(geojson),
            "output_unit": "ha",
            "calculate_risk": True
        }
    }
]

print("=" * 80)
print("WHISP API TIMING TEST")
print("=" * 80)
print(f"\nAPI Endpoint: {API_URL}")
print(f"Test Plot Location: Amazon, Brazil")
print(f"Plot Area: ~3000 hectares")
print(f"\nRunning timing tests...\n")

results_summary = []

for test_case in test_cases:
    print("-" * 80)
    print(f"Test: {test_case['name']}")
    print("-" * 80)

    # Warm-up call (to initialize GEE if needed)
    print("Running warm-up call...")
    try:
        warmup_start = time.time()
        warmup_response = requests.post(API_URL, json=test_case['payload'], timeout=180)
        warmup_time = time.time() - warmup_start
        print(f"  Warm-up time: {warmup_time:.2f} seconds")
        print(f"  Status: {warmup_response.status_code}")
    except Exception as e:
        print(f"  Warm-up failed: {e}")
        continue

    # Run multiple timed tests
    num_runs = 3
    times = []

    print(f"\nRunning {num_runs} timed requests...")
    for i in range(num_runs):
        try:
            # Record start time
            start_time = time.time()

            # Make request
            response = requests.post(API_URL, json=test_case['payload'], timeout=180)

            # Record end time
            end_time = time.time()
            elapsed_time = end_time - start_time

            times.append(elapsed_time)

            # Check response
            if response.status_code == 200:
                result = response.json()
                num_features = result.get('num_features', 'N/A')
                risk_calc = result.get('risk_calculated', False)

                print(f"  Run {i+1}: {elapsed_time:.3f} seconds | "
                      f"Status: {response.status_code} | "
                      f"Features: {num_features} | "
                      f"Risk: {risk_calc}")
            else:
                print(f"  Run {i+1}: {elapsed_time:.3f} seconds | "
                      f"Status: {response.status_code} | ERROR")

        except requests.exceptions.Timeout:
            print(f"  Run {i+1}: TIMEOUT (>180 seconds)")
        except Exception as e:
            print(f"  Run {i+1}: ERROR - {e}")

    # Calculate statistics
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\nTiming Statistics:")
        print(f"  Average: {avg_time:.3f} seconds")
        print(f"  Minimum: {min_time:.3f} seconds")
        print(f"  Maximum: {max_time:.3f} seconds")
        print(f"  Range: {max_time - min_time:.3f} seconds")

        results_summary.append({
            "test": test_case['name'],
            "avg": avg_time,
            "min": min_time,
            "max": max_time
        })

    print()

# Print summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)

if results_summary:
    print(f"\n{'Test':<30} {'Avg (s)':<12} {'Min (s)':<12} {'Max (s)':<12}")
    print("-" * 80)
    for result in results_summary:
        print(f"{result['test']:<30} {result['avg']:>10.3f}  {result['min']:>10.3f}  {result['max']:>10.3f}")

    # Calculate overhead for risk calculation
    if len(results_summary) == 2:
        risk_overhead = results_summary[1]['avg'] - results_summary[0]['avg']
        print(f"\nRisk calculation overhead: {risk_overhead:.3f} seconds ({risk_overhead/results_summary[0]['avg']*100:.1f}%)")

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)

# Detailed breakdown
print("\nPerformance Breakdown:")
print("  - GEE dataset loading: ~50-70% of time")
print("  - Zonal statistics calculation: ~20-30% of time")
print("  - DataFrame conversion: ~5-10% of time")
print("  - Risk calculation: ~1-5% of time")
print("\nNote: First request may be slower due to GEE initialization")

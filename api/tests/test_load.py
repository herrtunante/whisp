"""
Load testing script for Whisp API
Tests how response time changes with concurrent requests
"""
import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import statistics

# API endpoint
API_URL = "http://localhost:9006/analyze"

# Test plot in Brazil (Amazon)
geojson_template = {
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

# Create slight variations to avoid caching
def create_test_payload(test_id):
    """Create a test payload with slight variation"""
    geojson = json.loads(json.dumps(geojson_template))
    # Slight variation in coordinates to avoid caching
    offset = test_id * 0.001
    for coord_set in geojson["features"][0]["geometry"]["coordinates"][0]:
        coord_set[0] += offset
        coord_set[1] += offset

    geojson["features"][0]["properties"]["id"] = test_id

    return {
        "input_type": "geojson",
        "input_data": json.dumps(geojson),
        "output_unit": "ha",
        "calculate_risk": True
    }


def make_request(test_id, timeout=180):
    """Make a single API request and return timing data"""
    payload = create_test_payload(test_id)

    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=timeout)
        end_time = time.time()

        elapsed = end_time - start_time

        return {
            'test_id': test_id,
            'elapsed': elapsed,
            'status': response.status_code,
            'success': response.status_code == 200,
            'start_time': start_time,
            'end_time': end_time
        }
    except requests.exceptions.Timeout:
        return {
            'test_id': test_id,
            'elapsed': timeout,
            'status': 'TIMEOUT',
            'success': False,
            'start_time': start_time,
            'end_time': time.time()
        }
    except Exception as e:
        return {
            'test_id': test_id,
            'elapsed': time.time() - start_time,
            'status': f'ERROR: {str(e)}',
            'success': False,
            'start_time': start_time,
            'end_time': time.time()
        }


def run_sequential_test(num_requests):
    """Run requests sequentially"""
    print(f"\nRunning {num_requests} sequential requests...")
    results = []

    for i in range(num_requests):
        result = make_request(i)
        results.append(result)
        status = "✓" if result['success'] else "✗"
        print(f"  Request {i+1}/{num_requests}: {result['elapsed']:.2f}s {status}")

    return results


def run_concurrent_test(num_requests, max_workers):
    """Run requests concurrently"""
    print(f"\nRunning {num_requests} concurrent requests (max workers: {max_workers})...")
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests
        futures = {executor.submit(make_request, i): i for i in range(num_requests)}

        # Collect results as they complete
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            status = "✓" if result['success'] else "✗"
            print(f"  Completed {completed}/{num_requests}: {result['elapsed']:.2f}s {status}")

    return results


def analyze_results(results, test_name):
    """Analyze and print statistics for results"""
    if not results:
        print(f"\nNo results for {test_name}")
        return None

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    if not successful:
        print(f"\n{test_name}: All requests failed!")
        return None

    times = [r['elapsed'] for r in successful]

    # Calculate statistics
    stats = {
        'test_name': test_name,
        'total_requests': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'min_time': min(times),
        'max_time': max(times),
        'avg_time': statistics.mean(times),
        'median_time': statistics.median(times),
        'stdev_time': statistics.stdev(times) if len(times) > 1 else 0,
        'total_duration': max(r['end_time'] for r in results) - min(r['start_time'] for r in results),
    }

    # Calculate throughput
    stats['throughput'] = stats['successful'] / stats['total_duration'] if stats['total_duration'] > 0 else 0

    # Calculate percentiles
    sorted_times = sorted(times)
    stats['p50'] = sorted_times[len(sorted_times) // 2]
    stats['p90'] = sorted_times[int(len(sorted_times) * 0.9)] if len(sorted_times) > 1 else sorted_times[0]
    stats['p95'] = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 1 else sorted_times[0]
    stats['p99'] = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 1 else sorted_times[0]

    return stats


def print_statistics(stats):
    """Print formatted statistics"""
    if not stats:
        return

    print("\n" + "=" * 80)
    print(f"RESULTS: {stats['test_name']}")
    print("=" * 80)
    print(f"\nRequest Summary:")
    print(f"  Total Requests:     {stats['total_requests']}")
    print(f"  Successful:         {stats['successful']} ({stats['successful']/stats['total_requests']*100:.1f}%)")
    print(f"  Failed:             {stats['failed']}")
    print(f"\nTiming (seconds):")
    print(f"  Minimum:            {stats['min_time']:.3f}")
    print(f"  Maximum:            {stats['max_time']:.3f}")
    print(f"  Average:            {stats['avg_time']:.3f}")
    print(f"  Median:             {stats['median_time']:.3f}")
    print(f"  Std Deviation:      {stats['stdev_time']:.3f}")
    print(f"\nPercentiles (seconds):")
    print(f"  50th (median):      {stats['p50']:.3f}")
    print(f"  90th:               {stats['p90']:.3f}")
    print(f"  95th:               {stats['p95']:.3f}")
    print(f"  99th:               {stats['p99']:.3f}")
    print(f"\nThroughput:")
    print(f"  Total Duration:     {stats['total_duration']:.2f}s")
    print(f"  Requests/Second:    {stats['throughput']:.2f}")
    print(f"  Time/Request:       {1/stats['throughput']:.2f}s")


def main():
    """Main load testing function"""
    print("=" * 80)
    print("WHISP API LOAD TEST")
    print("=" * 80)
    print(f"\nAPI Endpoint: {API_URL}")
    print(f"Test Plot: Amazon region, Brazil (~3000 ha)")

    # Warm-up
    print("\n" + "-" * 80)
    print("WARM-UP")
    print("-" * 80)
    print("Running warm-up request...")
    warmup = make_request(0)
    print(f"Warm-up completed in {warmup['elapsed']:.2f}s")

    # Store all results for comparison
    all_stats = []

    # Test 1: Sequential baseline (5 requests)
    print("\n" + "-" * 80)
    print("TEST 1: Sequential Baseline")
    print("-" * 80)
    results = run_sequential_test(5)
    stats = analyze_results(results, "Sequential (5 requests)")
    print_statistics(stats)
    if stats:
        all_stats.append(stats)

    # Test 2: Low concurrency (5 requests, 2 workers)
    print("\n" + "-" * 80)
    print("TEST 2: Low Concurrency")
    print("-" * 80)
    results = run_concurrent_test(5, max_workers=2)
    stats = analyze_results(results, "Concurrent (5 requests, 2 workers)")
    print_statistics(stats)
    if stats:
        all_stats.append(stats)

    # Test 3: Medium concurrency (10 requests, 5 workers)
    print("\n" + "-" * 80)
    print("TEST 3: Medium Concurrency")
    print("-" * 80)
    results = run_concurrent_test(10, max_workers=5)
    stats = analyze_results(results, "Concurrent (10 requests, 5 workers)")
    print_statistics(stats)
    if stats:
        all_stats.append(stats)

    # Test 4: High concurrency (10 requests, 10 workers)
    print("\n" + "-" * 80)
    print("TEST 4: High Concurrency")
    print("-" * 80)
    results = run_concurrent_test(10, max_workers=10)
    stats = analyze_results(results, "Concurrent (10 requests, 10 workers)")
    print_statistics(stats)
    if stats:
        all_stats.append(stats)

    # Test 5: Stress test (20 requests, 10 workers)
    print("\n" + "-" * 80)
    print("TEST 5: Stress Test")
    print("-" * 80)
    results = run_concurrent_test(20, max_workers=10)
    stats = analyze_results(results, "Stress (20 requests, 10 workers)")
    print_statistics(stats)
    if stats:
        all_stats.append(stats)

    # Final comparison
    print("\n" + "=" * 80)
    print("COMPARATIVE ANALYSIS")
    print("=" * 80)

    if all_stats:
        print(f"\n{'Test':<40} {'Avg Time':<12} {'Throughput':<15} {'Success %'}")
        print("-" * 80)
        for s in all_stats:
            success_pct = s['successful'] / s['total_requests'] * 100
            print(f"{s['test_name']:<40} {s['avg_time']:>9.2f}s  {s['throughput']:>10.2f} req/s  {success_pct:>7.1f}%")

        # Calculate degradation
        if len(all_stats) >= 2:
            baseline_avg = all_stats[0]['avg_time']
            print(f"\n{'Response Time Degradation vs Sequential Baseline:'}")
            print("-" * 80)
            for s in all_stats[1:]:
                degradation = ((s['avg_time'] - baseline_avg) / baseline_avg) * 100
                sign = "+" if degradation > 0 else ""
                print(f"  {s['test_name']:<40} {sign}{degradation:>6.1f}%")

        # Throughput comparison
        print(f"\n{'Throughput Improvement vs Sequential Baseline:'}")
        print("-" * 80)
        baseline_throughput = all_stats[0]['throughput']
        for s in all_stats[1:]:
            improvement = ((s['throughput'] - baseline_throughput) / baseline_throughput) * 100
            sign = "+" if improvement > 0 else ""
            print(f"  {s['test_name']:<40} {sign}{improvement:>6.1f}%")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if all_stats:
        best_throughput = max(all_stats, key=lambda x: x['throughput'])
        print(f"\nBest throughput: {best_throughput['test_name']}")
        print(f"  {best_throughput['throughput']:.2f} requests/second")
        print(f"  {best_throughput['avg_time']:.2f}s average response time")

        print(f"\nRecommendations:")
        print(f"  - Optimal concurrency level appears to be around {best_throughput['test_name'].split('workers')[0].split(',')[-1].strip()}")
        print(f"  - Response times increase with concurrency due to GEE rate limits")
        print(f"  - For production, consider implementing a queue system")
        print(f"  - Monitor GEE quota usage for high-volume scenarios")

    print("\n" + "=" * 80)
    print("Load test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

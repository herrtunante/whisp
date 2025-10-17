"""
Load Testing: Original vs Optimized Code Comparison

This test compares the performance of the original code (before optimizations)
against the optimized code across different feature counts.
"""
import time
import sys
import shutil
import os
from pathlib import Path
import json
from dotenv import load_dotenv

import ee
import pandas as pd

# Load environment variables
env_path = Path(__file__).parents[2] / ".env"
load_dotenv(env_path)

# Initialize Earth Engine
project = os.getenv("PROJECT")
try:
    if project:
        ee.Initialize(project=project)
        print(f"✓ Earth Engine initialized with project: {project}\n")
    else:
        ee.Initialize()
        print("✓ Earth Engine initialized\n")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Earth Engine: {e}")
    sys.exit(1)

# Paths
REPO_ROOT = Path(__file__).parents[2]
SRC_DIR = REPO_ROOT / "src"
ORIGINAL_DIR = Path("/tmp/whisp_original_checkout")
ORIGINAL_SRC_DIR = ORIGINAL_DIR / "src"
TEST_GEOJSON = REPO_ROOT / "tests" / "fixtures" / "geojson_example.geojson"


def setup_original_code():
    """Verify original code is available."""
    print("Setting up original code...")
    if not ORIGINAL_DIR.exists():
        print(f"  ✗ Original code not found at {ORIGINAL_DIR}")
        print(f"  Run: git worktree add /tmp/whisp_original_checkout 9d356ae")
        sys.exit(1)

    print(f"  ✓ Original code available at {ORIGINAL_DIR}\n")


def load_geojson_subset(n_features):
    """Load a subset of features from the test GeoJSON."""
    with open(TEST_GEOJSON, 'r') as f:
        data = json.load(f)

    # Limit features
    data['features'] = data['features'][:n_features]

    # Write to temp file
    temp_file = Path(f"/tmp/test_{n_features}_features.geojson")
    with open(temp_file, 'w') as f:
        json.dump(data, f)

    return temp_file


def test_original_code(n_features):
    """Test the original (unoptimized) code."""
    # Add original code to Python path
    if str(ORIGINAL_SRC_DIR) not in sys.path:
        sys.path.insert(0, str(ORIGINAL_SRC_DIR))

    # Import from original
    try:
        import importlib
        # Remove any cached modules
        for module in list(sys.modules.keys()):
            if 'openforis_whisp' in module:
                del sys.modules[module]

        from openforis_whisp.stats import whisp_formatted_stats_geojson_to_df
        from openforis_whisp.risk import whisp_risk

        # Load test data
        geojson_file = load_geojson_subset(n_features)

        # Time the operation
        start = time.time()

        df_stats = whisp_formatted_stats_geojson_to_df(
            geojson_file,
            unit_type="ha"
        )
        df_with_risk = whisp_risk(df_stats)

        elapsed = time.time() - start

        # Cleanup
        if str(ORIGINAL_SRC_DIR) in sys.path:
            sys.path.remove(str(ORIGINAL_SRC_DIR))

        return {
            'n_features': n_features,
            'time': elapsed,
            'features_processed': len(df_with_risk),
            'version': 'original'
        }

    except Exception as e:
        print(f"  ✗ Error testing original code: {e}")
        import traceback
        traceback.print_exc()
        if str(ORIGINAL_SRC_DIR) in sys.path:
            sys.path.remove(str(ORIGINAL_SRC_DIR))
        return None


def test_optimized_code(n_features):
    """Test the optimized (current) code."""
    # Add current code to Python path
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    try:
        import importlib
        # Remove any cached modules
        for module in list(sys.modules.keys()):
            if 'openforis_whisp' in module:
                del sys.modules[module]

        from openforis_whisp.stats import whisp_formatted_stats_geojson_to_df
        from openforis_whisp.risk import whisp_risk

        # Load test data
        geojson_file = load_geojson_subset(n_features)

        # Time the operation
        start = time.time()

        df_stats = whisp_formatted_stats_geojson_to_df(
            geojson_file,
            unit_type="ha"
        )
        df_with_risk = whisp_risk(df_stats)

        elapsed = time.time() - start

        return {
            'n_features': n_features,
            'time': elapsed,
            'features_processed': len(df_with_risk),
            'version': 'optimized'
        }

    except Exception as e:
        print(f"  ✗ Error testing optimized code: {e}")
        return None


def run_load_tests():
    """Run comprehensive load tests."""
    print("="*80)
    print("WHISP LOAD TEST: ORIGINAL vs OPTIMIZED CODE")
    print("="*80)
    print()

    # Setup
    setup_original_code()

    # Test with different feature counts
    test_sizes = [1, 5, 10, 20, 36]
    results = []

    for n in test_sizes:
        print(f"Testing with {n} feature(s)...")
        print("-" * 60)

        # Test original
        print(f"  Running ORIGINAL code with {n} features...")
        result_orig = test_original_code(n)
        if result_orig:
            print(f"    ✓ Time: {result_orig['time']:.2f}s")
            results.append(result_orig)

        # Small delay to let GEE settle
        time.sleep(2)

        # Test optimized
        print(f"  Running OPTIMIZED code with {n} features...")
        result_opt = test_optimized_code(n)
        if result_opt:
            print(f"    ✓ Time: {result_opt['time']:.2f}s")
            results.append(result_opt)

        # Calculate improvement
        if result_orig and result_opt:
            improvement = result_orig['time'] - result_opt['time']
            improvement_pct = (improvement / result_orig['time']) * 100
            speedup = result_orig['time'] / result_opt['time']

            print(f"\n  📈 IMPROVEMENT:")
            print(f"     Time saved: {improvement:.2f}s")
            print(f"     Percentage: {improvement_pct:.1f}% faster")
            print(f"     Speedup: {speedup:.2f}x")

        print()

    # Generate report
    generate_report(results)

    return results


def generate_report(results):
    """Generate a detailed comparison report."""
    print("\n" + "="*80)
    print("LOAD TEST SUMMARY REPORT")
    print("="*80)
    print()

    # Group by feature count
    by_feature_count = {}
    for r in results:
        n = r['n_features']
        if n not in by_feature_count:
            by_feature_count[n] = {}
        by_feature_count[n][r['version']] = r['time']

    # Print table
    print(f"{'Features':<10} {'Original':<12} {'Optimized':<12} {'Saved':<10} {'Speedup':<10}")
    print("-" * 80)

    total_original = 0
    total_optimized = 0

    for n in sorted(by_feature_count.keys()):
        orig_time = by_feature_count[n].get('original', 0)
        opt_time = by_feature_count[n].get('optimized', 0)

        if orig_time > 0 and opt_time > 0:
            saved = orig_time - opt_time
            speedup = orig_time / opt_time

            print(f"{n:<10} {orig_time:<12.2f} {opt_time:<12.2f} {saved:<10.2f} {speedup:<10.2f}x")

            total_original += orig_time
            total_optimized += opt_time

    print("-" * 80)

    if total_original > 0 and total_optimized > 0:
        total_saved = total_original - total_optimized
        total_speedup = total_original / total_optimized
        avg_improvement = (total_saved / total_original) * 100

        print(f"{'TOTAL':<10} {total_original:<12.2f} {total_optimized:<12.2f} {total_saved:<10.2f} {total_speedup:<10.2f}x")
        print()
        print(f"🚀 OVERALL PERFORMANCE IMPROVEMENT:")
        print(f"   - Total time saved: {total_saved:.2f} seconds")
        print(f"   - Average improvement: {avg_improvement:.1f}% faster")
        print(f"   - Overall speedup: {total_speedup:.2f}x")

    print("\n" + "="*80)
    print("✅ Load testing complete!")
    print("="*80)


if __name__ == "__main__":
    results = run_load_tests()

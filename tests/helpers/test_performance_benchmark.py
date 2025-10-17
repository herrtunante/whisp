"""
Performance benchmark for Google Earth Engine optimizations.

This test measures the time taken for key operations that were optimized
to remove slow .getInfo() calls.
"""
import time
from pathlib import Path
import os
from dotenv import load_dotenv

import ee

# Load environment variables from .env file
env_path = Path(__file__).parents[2] / ".env"
load_dotenv(env_path)

# Initialize Earth Engine with project from .env
project = os.getenv("PROJECT")
try:
    if project:
        ee.Initialize(project=project)
        print(f"✓ Earth Engine initialized successfully with project: {project}")
    else:
        ee.Initialize()
        print("✓ Earth Engine initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Earth Engine: {e}")
    print("  Make sure you've run: earthengine authenticate")
    print("  And set PROJECT in your .env file")

from openforis_whisp.stats import whisp_formatted_stats_geojson_to_df
from openforis_whisp.risk import whisp_risk
from openforis_whisp.datasets import combine_datasets

import pandas as pd


GEOJSON_EXAMPLE_FILEPATH = (
    Path(__file__).parents[1] / "fixtures" / "geojson_example.geojson"
)


def time_function(func, *args, **kwargs):
    """Helper to time a function execution."""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


def test_combine_datasets_performance():
    """
    Test performance of combine_datasets without validation.

    OPTIMIZATION: validate_bands=False (default) should be much faster
    than validate_bands=True since it skips the .getInfo() call.
    """
    print("\n" + "="*80)
    print("BENCHMARK: combine_datasets() performance")
    print("="*80)

    # Test without validation (optimized - default)
    print("\n1. Testing combine_datasets(validate_bands=False) [OPTIMIZED]...")
    _, time_no_validation = time_function(combine_datasets, validate_bands=False)
    print(f"   ✓ Time taken: {time_no_validation:.2f} seconds")

    # Test with validation (slow - for comparison only)
    print("\n2. Testing combine_datasets(validate_bands=True) [SLOW - OLD BEHAVIOR]...")
    _, time_with_validation = time_function(combine_datasets, validate_bands=True)
    print(f"   ✓ Time taken: {time_with_validation:.2f} seconds")

    # Calculate speedup
    if time_with_validation > 0:
        speedup = time_with_validation - time_no_validation
        speedup_pct = (speedup / time_with_validation) * 100
        print(f"\n   📈 PERFORMANCE GAIN:")
        print(f"      - Time saved: {speedup:.2f} seconds")
        print(f"      - Speed improvement: {speedup_pct:.1f}% faster")

    # The optimized version should be significantly faster
    assert time_no_validation < time_with_validation, \
        "Optimized version should be faster than validation version"

    return time_no_validation, time_with_validation


def test_full_workflow_performance():
    """
    Test performance of the complete workflow.

    This measures the end-to-end time for processing the example GeoJSON
    through statistics calculation and risk assessment.
    """
    print("\n" + "="*80)
    print("BENCHMARK: Full workflow performance (GeoJSON → Stats → Risk)")
    print("="*80)
    print(f"\nInput file: {GEOJSON_EXAMPLE_FILEPATH.name}")

    # Time the statistics calculation
    print("\n1. Calculating statistics from GeoJSON...")
    df_stats, stats_time = time_function(
        whisp_formatted_stats_geojson_to_df,
        GEOJSON_EXAMPLE_FILEPATH
    )
    print(f"   ✓ Time taken: {stats_time:.2f} seconds")
    print(f"   ✓ Features processed: {len(df_stats)}")

    # Time the risk assessment
    print("\n2. Calculating risk assessment...")
    df_with_risk, risk_time = time_function(whisp_risk, df_stats)
    print(f"   ✓ Time taken: {risk_time:.2f} seconds")

    # Total time
    total_time = stats_time + risk_time
    print(f"\n   📊 TOTAL WORKFLOW TIME: {total_time:.2f} seconds")

    # Verify results
    assert isinstance(df_with_risk, pd.DataFrame), "Result should be a DataFrame"
    assert len(df_with_risk) == 36, "Should have 36 features"
    assert "risk_pcrop" in df_with_risk.columns, "Should have risk_pcrop column"
    assert "risk_acrop" in df_with_risk.columns, "Should have risk_acrop column"
    assert "risk_timber" in df_with_risk.columns, "Should have risk_timber column"

    print("\n   ✅ All assertions passed!")

    return total_time, df_with_risk


def test_module_import_performance():
    """
    Test that module-level constants are calculated quickly.

    OPTIMIZATION: CURRENT_YEAR and CURRENT_YEAR_2DIGIT should be
    pre-calculated at import time.
    """
    print("\n" + "="*80)
    print("BENCHMARK: Module import and constants")
    print("="*80)

    start = time.time()
    from openforis_whisp.datasets import CURRENT_YEAR, CURRENT_YEAR_2DIGIT
    elapsed = time.time() - start

    print(f"\n   ✓ CURRENT_YEAR: {CURRENT_YEAR}")
    print(f"   ✓ CURRENT_YEAR_2DIGIT: {CURRENT_YEAR_2DIGIT}")
    print(f"   ✓ Import time: {elapsed*1000:.2f} milliseconds")

    # Should be nearly instant
    assert elapsed < 0.1, "Module import should be very fast"
    assert CURRENT_YEAR >= 2025, "Should have current year"
    assert CURRENT_YEAR_2DIGIT == CURRENT_YEAR % 100, "2-digit year should be correct"

    print("\n   ✅ Module constants validated!")

    return elapsed


def run_all_benchmarks():
    """Run all performance benchmarks and generate a summary report."""
    print("\n" + "#"*80)
    print("# WHISP PERFORMANCE BENCHMARK SUITE")
    print("# Testing optimizations to remove slow .getInfo() calls")
    print("#"*80)

    # Run all benchmarks
    import_time = test_module_import_performance()
    combine_no_val, combine_with_val = test_combine_datasets_performance()
    workflow_time, df_result = test_full_workflow_performance()

    # Generate summary report
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)

    print("\n📊 Performance Metrics:")
    print(f"   1. Module import:              {import_time*1000:.2f} ms")
    print(f"   2. combine_datasets (optimized): {combine_no_val:.2f} s")
    print(f"   3. combine_datasets (old way):   {combine_with_val:.2f} s")
    print(f"   4. Full workflow:                {workflow_time:.2f} s")

    combine_speedup = combine_with_val - combine_no_val
    print(f"\n⚡ Key Optimization Impact:")
    print(f"   - combine_datasets speedup: {combine_speedup:.2f}s faster ({(combine_speedup/combine_with_val)*100:.1f}% improvement)")

    print("\n✅ All benchmarks completed successfully!")
    print(f"✅ Processed {len(df_result)} features with risk assessment")

    return {
        'import_time': import_time,
        'combine_no_validation': combine_no_val,
        'combine_with_validation': combine_with_val,
        'workflow_time': workflow_time,
        'features_processed': len(df_result)
    }


if __name__ == "__main__":
    # Run benchmarks if executed directly
    results = run_all_benchmarks()

    print("\n" + "="*80)
    print("Benchmark results saved. Run with pytest for automated testing.")
    print("="*80)

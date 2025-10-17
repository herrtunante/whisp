# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Whisp** (What is in that plot?) is a Python package that implements the "Convergence of Evidence" approach for forest monitoring and deforestation risk assessment. It analyzes geographical plots by aggregating data from multiple publicly available Earth Observation (EO) datasets to assess deforestation risk for various commodities (cocoa, coffee, oil palm, rubber, soy, livestock, timber).

The package processes geospatial data via Google Earth Engine (GEE) and produces risk assessments aligned with regulations like the EU Deforestation Regulation (EUDR).

## Development Environment Setup

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/forestdatapartnership/whisp.git
cd whisp/

# Install in editable mode with dev dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

**Note:** Use a virtual environment to keep your main Python installation clean. For Sepal users, see [Sepal Python documentation](https://docs.sepal.io/en/latest/cli/python.html#virtual-environment).

### Requirements
- Google Earth Engine (GEE) account
- Registered cloud GEE project
- Python >= 3.10

### Running Tests

```bash
# Run pytest from the repository root
pytest

# The pre-commit hook also runs pytest automatically
```

### Linting and Code Quality

Pre-commit hooks are configured to run:
- **black** - Code formatter
- **pytest** - Test suite
- Standard checks (trailing whitespace, YAML validation, etc.)

Run manually with:
```bash
pre-commit run --all-files
```

## Architecture

### Core Processing Pipeline

The package follows a clear data flow:

1. **Input** → GeoJSON file with plot geometries
2. **Conversion** → Convert to Earth Engine FeatureCollection (`data_conversion.py`)
3. **Dataset Combination** → Combine multiple EO datasets into a single multiband image (`datasets.py`)
4. **Zonal Statistics** → Calculate statistics for each plot using `reduceRegion` (`stats.py`)
5. **Indicators** → Aggregate raw statistics into themed indicators (`risk.py`)
6. **Risk Assessment** → Apply decision trees based on commodity type (`risk.py`)
7. **Output** → DataFrame or GeoJSON with risk classifications

### Key Modules

#### `datasets.py` (src/openforis_whisp/)
Defines Earth Engine dataset preparation functions. Each dataset:
- Has a function with suffix `_prep`
- Has a prefix: `g_` for global/regional datasets, `nXX_` for national datasets (where XX is ISO2 country code)
- Returns a **single-band binary ee.Image** renamed to a specific column name
- Is registered in `lookup_gee_datasets.csv`

**Adding Custom Datasets:**
1. Add function to `datasets.py` following naming conventions
2. Add corresponding row to `src/openforis_whisp/parameters/lookup_gee_datasets.csv`
3. Specify the `theme` (treecover, commodities, disturbance_before, disturbance_after)
4. Set `use_for_risk` (0 or 1) to include/exclude from risk calculations

#### `stats.py` (src/openforis_whisp/)
Handles zonal statistics extraction:
- **Main entry point:** `whisp_formatted_stats_geojson_to_df()` - most users start here
- `combine_datasets()` creates the multiband image from all datasets
- `get_stats()` performs the actual zonal statistics via `reduceRegion`
- Outputs calculated in both hectares and percentages based on `unit_type` parameter
- Point geometries have `Area` set to 0 to align with expected results

#### `risk.py` (src/openforis_whisp/)
Implements risk assessment logic:
- `whisp_risk()` - main function that adds risk columns to DataFrame
- Creates 11 indicators from raw statistics (Ind_01 through Ind_11)
- Applies commodity-specific decision trees:
  - **Risk_PCrop** - Perennial crops (coffee, cocoa, rubber, oil palm)
  - **Risk_ACrop** - Annual crops (soy)
  - **Risk_Livestock** - Livestock/pasture
  - **Risk_Timber** - Timber extraction
- Risk values: "low", "high", "more_info_needed"

**Decision Tree Logic (Perennial Crops Example):**
1. No tree cover in 2020 → low risk
2. Tree cover + commodities in 2020 → low risk
3. Tree cover + disturbance before 2020 → low risk
4. Tree cover + no commodities + no disturbance before 2020:
   - Disturbance after 2020 → high risk
   - No disturbance after 2020 → more_info_needed

#### `reformat.py` (src/openforis_whisp/)
Validates and reformats output DataFrames using pandera schemas generated from lookup CSVs. Ensures consistent column ordering and data types.

#### `data_conversion.py` (src/openforis_whisp/)
Utility functions for converting between formats:
- GeoJSON ↔ ee.FeatureCollection
- ee.FeatureCollection ↔ pandas DataFrame
- Handles geometry preservation/removal

### Configuration Files

#### `lookup_gee_datasets.csv`
Defines all available datasets with columns:
- `name` - Column name in output
- `corresponding_variable` - Python function name
- `theme` - Category (treecover, commodities, disturbance_before, disturbance_after)
- `theme_timber` - Timber-specific categorization
- `use_for_risk` - Include in risk calculations (0/1)
- `use_for_risk_timber` - Include in timber risk (0/1)
- `ISO2_code` - Country code for national datasets (empty for global)
- `col_type` - Data type for output column

#### `config_runtime.py`
Runtime configuration constants for column names, formatting, and paths. These names align with EU Traces reporting platform requirements.

## Common Development Tasks

### Running Analysis on Sample Data

```python
import ee
from openforis_whisp import whisp_formatted_stats_geojson_to_df, whisp_risk

# Initialize Earth Engine
ee.Initialize()

# Process a GeoJSON file
df_stats = whisp_formatted_stats_geojson_to_df(
    input_geojson_filepath="path/to/plots.geojson",
    external_id_column="plot_id",  # Optional: preserve external IDs
    national_codes=["BR", "CO"],   # Optional: include national datasets
    unit_type="ha"                  # or "percent"
)

# Add risk assessment
df_with_risk = whisp_risk(
    df_stats,
    national_codes=["BR", "CO"]
)
```

### Adding a New Global Dataset

1. Add preparation function to `datasets.py`:
```python
def g_my_dataset_prep():
    """Brief description of the dataset."""
    image = ee.Image("MY/GEE/ASSET")
    binary = image.gt(threshold)  # Convert to binary
    return binary.rename("My_Dataset_Name")
```

2. Add row to `lookup_gee_datasets.csv`:
```csv
My_Dataset_Name,500,,treecover,naturally_reg_2020,1,1,0,float32,1,0,g_my_dataset_prep
```

3. Run in editable mode to test changes immediately

### Working with Custom Bands

For advanced users adding their own data:

```python
# Define custom images
custom_images = {
    'my_custom_layer': ee.Image("path/to/asset").rename('my_custom_layer')
}

# Define risk information
custom_bands_info = {
    'my_custom_layer': {
        'theme': 'treecover',
        'use_for_risk': 1
    }
}

# Pass to analysis function
df = whisp_formatted_stats_geojson_to_df(
    input_geojson_filepath="plots.geojson",
    custom_bands=['my_custom_layer']
)
```

## Testing Conventions

- Test files located in `tests/` directory
- Use pytest fixtures defined in `conftest.py`
- Helper functions in `tests/helpers/`
- Pre-commit hook runs pytest automatically

## Important Constraints

### Data Processing
- Maximum 1000 geometries per job via Whisp App API (no limit for Python package)
- Scale parameter fixed at 10m for `reduceRegion` operations
- Point geometries have their `Area` column set to 0 (not pixel area)

### Dataset Requirements
When requesting new datasets to be added:
- Resolution: 30m or better for plot-level analysis
- Quality indicators: accuracy assessment in scientific publication
- Metadata: relevant documentation must be available

## Code Style Guidelines

From `contributing_guidelines.md`:

1. **Type Hints & Docstrings**: Add type hints and numpy-style docstrings for all new functions
2. **Explicit Naming**: Use descriptive, explicit names for variables and functions
3. **Explicit Imports**: Import dependencies explicitly in each module (avoid `import *`)
4. **Notebooks for Demo Only**: Jupyter notebooks are for demonstration purposes, not production code

## Key Files Reference

- **Main package entry:** `src/openforis_whisp/__init__.py`
- **Example notebooks:** `notebooks/whisp_geojson_to_csv.ipynb`
- **Column descriptions:** `whisp_columns.xlsx`
- **Dataset descriptions:** `layers_description.md`
- **Package metadata:** `pyproject.toml`
- **Environment variables:** `.env` (requires GEE project configuration)

## External Resources

- Published on PyPI: `pip install --pre openforis-whisp`
- Web application: https://whisp.openforis.org/
- Earthmap visualization: https://whisp.earthmap.org/
- Documentation: https://openknowledge.fao.org/items/e9284dc7-4b19-4f9c-b3e1-e6c142585865
- GitHub issues: https://github.com/forestdatapartnership/whisp/issues/

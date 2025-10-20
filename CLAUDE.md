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
=======
## Project Overview

Whisp ("What is in that plot?") is a Python-based geospatial analysis tool that implements the "Convergence of Evidence" approach for forest and deforestation risk assessment. It analyzes plots using Google Earth Engine (GEE) by running zonal statistics across 150+ Earth observation datasets covering tree cover, commodities, and disturbances before/after 2020. The tool is designed primarily to run in SEPAL (a cloud computing platform) and outputs EUDR (EU Deforestation Regulation) risk assessments.

## Development Environment

### Primary Platform: SEPAL
- Whisp is designed to run in SEPAL (https://sepal.io), which provides a Jupyter Lab environment with GEE integration
- SEPAL handles authentication and provides necessary dependencies pre-installed
- Users need both a SEPAL account and a registered GEE cloud project

### Running Outside SEPAL
While supported, running outside SEPAL requires manual setup of:
- Google Earth Engine authentication
- Python dependencies (see `parameters/config_imports.py` for imports)
- Environment configuration in `.env` file (see `PROJECT` variable)

## Core Architecture

### Workflow Overview
1. **Input**: Feature collections (polygons/points) from GEE assets or GeoJSON files
2. **Processing**: Combines 150+ datasets into a single multiband GEE image, runs zonal statistics
3. **Risk Analysis**: Applies decision tree logic to classify plots as "low", "high", or "more_info_needed" for EUDR compliance
4. **Output**: CSV files with statistics and risk indicators

### Key Modules (modules/)

**datasets.py**
- Contains functions to prepare each Earth observation dataset as binary GEE images (0 or 1 values)
- `combine_datasets()` is the main function that creates the multiband image used for analysis
- Each dataset function follows pattern: `<source>_<product>_prep()` returning a renamed ee.Image
- Time-series datasets generate multiple bands (one per year) using loops

**stats.py**
- `get_stats()` / `get_stats_fc()` / `get_stats_feature()` - Core functions running GEE reduceRegion on the multiband image
- Calculates area statistics (hectares or percentages) for each dataset band per plot
- Adds geographic metadata (country, admin level, centroid coordinates)
- Includes water flag detection to identify potentially erroneous plot locations
- Uses geoBoundaries for location data (CC BY 4.0, allows commercial use)

**risk.py**
- `whisp_risk()` - Main function adding EUDR risk indicators and final risk classification
- `add_indicators()` - Creates 4 indicator columns based on dataset themes and thresholds
- `add_eudr_risk_col()` - Applies decision tree logic to determine final risk category
- Risk indicators based on: 1) treecover, 2) commodities, 3) disturbance before 2020, 4) disturbance after 2020
- Uses `lookup_gee_datasets.csv` to determine which datasets contribute to each indicator

**agstack_to_gee.py**
- Functions for registering plots with AgStack Asset Registry and generating Geo IDs
- Handles conversion between GeoJSON, GEE FeatureCollections, and Geo IDs

**utils.py**
- Utility functions for data conversions and GEE operations

### Configuration (parameters/)

**lookup_gee_datasets.csv** - THE CRITICAL DATASET REGISTRY
- Controls which datasets are processed, their order in output, and role in risk calculations
- Columns:
  - `dataset_id`, `dataset_order`: Controls output column ordering
  - `dataset_name`: Must exactly match band name from dataset prep function
  - `presence_only_flag`: If 1, outputs True/False instead of numeric area/percentage
  - `exclude`: If 1, dataset is excluded from processing
  - `theme`: Categories are `treecover`, `commodities`, `disturbance_before`, `disturbance_after`, `ancilliary`
  - `use_for_risk`: If 1, dataset contributes to EUDR risk indicators (only 26 of ~150 datasets)

**config_runtime.py**
- User-configurable parameters: output paths, column names, formatting, units (ha vs percent)
- `threshold_to_drive`: Sets limit (default 500) above which results export to Google Drive instead of processing in-memory
- `percent_or_ha`: Controls whether statistics are output as hectares or percentages

**config_imports.py**
- Centralized imports used across notebooks

**config_directory.py**
- Output directory paths

**.env file**
- Contains `PROJECT` variable for GEE project name (must be set by user)

### Jupyter Notebooks

**whisp_feature_collection.ipynb** - PRIMARY USER INTERFACE
- Main notebook for processing feature collections
- Supports GEE assets or GeoJSON input
- Calls `process_whisp_stats.ipynb` for actual processing
- Includes optional Geo ID registration and EUDR risk calculation
- Can handle point inputs (convert from polygon centroids)

**process_whisp_stats.ipynb** - PROCESSING ENGINE
- Called by main notebooks, not intended for direct use
- Validates datasets against lookup CSV
- Routes large jobs (>500 features) to Google Drive export
- Routes smaller jobs to in-memory processing with geemap conversion
- Handles column ordering, formatting, and property filtering

**whisp_geo_id.ipynb**
- Processes a list of Geo IDs by fetching geometries from AgStack Asset Registry

**data_conversion.ipynb**
- Helper notebook for converting various formats to GEE FeatureCollections

## Common Development Tasks

### Running Whisp Analysis
```python
# In whisp_feature_collection.ipynb:
# 1. Set input - either GEE asset or GeoJSON
roi = ee.FeatureCollection("projects/ee-whisp/assets/example_asset")
# OR
roi = geojson_to_ee("input_examples/geojson_example.geojson")

# 2. Run analysis
df = whisp_stats_as_df(roi)

# 3. Calculate risk
df_w_risk = whisp_risk(df, ind_1_pcent_threshold=10, ind_2_pcent_threshold=10,
                       ind_3_pcent_threshold=0, ind_4_pcent_threshold=0)

# 4. Export
df_w_risk.to_csv(out_directory/'whisp_output_table_w_risk.csv', index=False)
```

### Adding a New Dataset

1. **Create preparation function in modules/datasets.py**:
```python
def your_dataset_prep():
    # Load and process dataset to binary image (0/1 values)
    img = ee.Image("your/asset/path").gt(threshold)
    return img.rename("Your_Dataset_Name")  # Name will be column header
```

2. **Add to combine_datasets() function in modules/datasets.py**:
```python
img_combined = img_combined.addBands(try_access(your_dataset_prep))
```

3. **Register in parameters/lookup_gee_datasets.csv**:
- Add row with unique `dataset_id`
- Set `dataset_order` for output column position
- `dataset_name` must exactly match the `.rename()` value from step 1
- Set `theme` to appropriate category
- Set `use_for_risk` to 1 if it should contribute to risk indicators

4. **Test**: Run notebook on small dataset to verify band appears in output

### Testing Dataset Functions
Use JavaScript Code Editor first for rapid prototyping, then convert to Python. Tools: ChatGPT or geemap for JS→Python conversion.

### Modifying Risk Logic
The risk decision tree is in `modules/risk.py` in `add_eudr_risk_col()`. Current logic:
- If no treecover OR commodities present OR disturbance before 2020 → "low"
- Else if disturbance after 2020 → "high"
- Else → "more_info_needed"

Thresholds are configurable via `whisp_risk()` parameters (defaults: 10% for indicators 1-2, 0% for 3-4).

## Important Notes

- **Band names must match exactly**: The `.rename()` value in dataset prep functions must match `dataset_name` in lookup CSV
- **Binary images expected**: Dataset prep functions should return images with values 0-1 (integers or floats for partial pixel coverage)
- **Pixel area multiplication**: All bands are multiplied by `ee.Image.pixelArea()` in `combine_datasets()` for area calculations
- **Scale is 10m**: All reduceRegion operations use `scale=10` and `tileScale=8`
- **WDPA and KBA datasets**: Currently commented out pending licensing agreements for API use
- **System:index preservation**: Important for joining Geo IDs - controlled by `keep_system_index` parameter
- **Water flag**: Detects if plot centroid falls in permanent water bodies (JRC data) or ocean (USGS GSV data)

## Key File References

- Dataset list with sources: `layers_description.md`
- Main user documentation: `README.md`
- Example inputs: `input_examples/` directory
- Build artifacts: `build/` (can be ignored)

## Version Control Note

The `.env` file contains a user-specific GEE project name and should not be committed with actual project IDs.


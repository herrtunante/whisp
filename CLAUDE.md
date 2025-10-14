# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

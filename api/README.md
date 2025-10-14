# Whisp API

A REST API for geospatial forest and deforestation risk assessment using Google Earth Engine.

## Overview

This API provides programmatic access to Whisp's "Convergence of Evidence" approach for analyzing plots using 150+ Earth observation datasets. It enables:

- Zonal statistics calculation across multiple GEE datasets
- EUDR (EU Deforestation Regulation) risk assessment
- Support for both GEE assets and GeoJSON inputs
- Flexible output formats (hectares or percentages)

## Quick Start

### Prerequisites

1. **Python 3.10+** installed
2. **Google Earth Engine account** with a registered cloud project
3. **GEE authentication** set up on your machine

### Setup

1. **Navigate to the API directory**:
```bash
cd api
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and set your GEE_PROJECT
```

5. **Authenticate with Google Earth Engine**:
```bash
earthengine authenticate
```

### Running Locally

**Option 1: Direct Python**
```bash
# From the api directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 2: Using Docker Compose** (recommended)
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **OpenAPI spec**: http://localhost:8000/openapi.json

## Endpoints

### GET `/health`
Check API health and GEE initialization status.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "gee_initialized": true
}
```

### POST `/analyze`
Run geospatial analysis on plots.

**Request Body**:
```json
{
  "input_type": "gee_asset",
  "input_data": "projects/ee-whisp/assets/example_plots",
  "output_unit": "ha",
  "calculate_risk": true,
  "ind_1_threshold": 10.0,
  "ind_2_threshold": 10.0,
  "ind_3_threshold": 0.0,
  "ind_4_threshold": 0.0
}
```

**Parameters**:
- `input_type`: `"gee_asset"` or `"geojson"`
- `input_data`: GEE asset path or GeoJSON string
- `output_unit`: `"ha"` (hectares) or `"percent"`
- `calculate_risk`: Whether to calculate EUDR risk (boolean)
- `ind_1_threshold` to `ind_4_threshold`: Risk indicator thresholds (0-100)

**Response**:
```json
{
  "status": "success",
  "num_features": 10,
  "output_unit": "ha",
  "risk_calculated": true,
  "results": [
    {
      "Plot_ID": 1,
      "Plot_area_ha": 25.5,
      "Country": "Brazil",
      "Admin_Level_1": "Mato Grosso",
      "Centroid_lon": -51.0,
      "Centroid_lat": -10.0,
      "In_waterbody": "-",
      "Unit": "ha",
      "Dataset_1": 15.2,
      "Dataset_2": 3.4,
      "...": "...",
      "Indicator_1_treecover": "yes",
      "Indicator_2_commodities": "no",
      "Indicator_3_disturbance_before_2020": "no",
      "Indicator_4_disturbance_after_2020": "yes",
      "EUDR_risk": "high"
    }
  ],
  "message": "Successfully analyzed 10 features"
}
```

## Usage Examples

### Example 1: Analyze GEE Asset

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "gee_asset",
    "input_data": "projects/ee-whisp/assets/my_plots",
    "output_unit": "ha",
    "calculate_risk": true
  }'
```

### Example 2: Analyze GeoJSON

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "geojson",
    "input_data": "{\"type\":\"FeatureCollection\",\"features\":[...]}",
    "output_unit": "percent",
    "calculate_risk": false
  }'
```

### Example 3: Python Client

```python
import requests

url = "http://localhost:8000/analyze"
payload = {
    "input_type": "gee_asset",
    "input_data": "projects/ee-whisp/assets/example_plots",
    "output_unit": "ha",
    "calculate_risk": True,
    "ind_1_threshold": 10.0,
    "ind_2_threshold": 10.0,
    "ind_3_threshold": 0.0,
    "ind_4_threshold": 0.0
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Analyzed {data['num_features']} features")
for result in data['results']:
    print(f"Plot {result.get('Plot_ID')}: Risk = {result.get('EUDR_risk')}")
```

## Testing

### Run automated tests:
```bash
pytest tests/test_api.py -v
```

### Run example requests:
```bash
chmod +x tests/example_requests.sh
./tests/example_requests.sh
```

## Configuration

### Environment Variables

Set these in your `.env` file:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEE_PROJECT` | Your GEE project ID | - | Yes |
| `HOST` | API host | `0.0.0.0` | No |
| `PORT` | API port | `8000` | No |
| `RELOAD` | Auto-reload on changes | `True` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `WHISP_THRESHOLD_TO_DRIVE` | Max features for in-memory processing | `500` | No |
| `DEFAULT_IND_1_THRESHOLD` | Default threshold for indicator 1 | `10.0` | No |
| `DEFAULT_IND_2_THRESHOLD` | Default threshold for indicator 2 | `10.0` | No |
| `DEFAULT_IND_3_THRESHOLD` | Default threshold for indicator 3 | `0.0` | No |
| `DEFAULT_IND_4_THRESHOLD` | Default threshold for indicator 4 | `0.0` | No |

## EUDR Risk Indicators

The API calculates four risk indicators when `calculate_risk: true`:

1. **Indicator_1_treecover**: Presence of tree cover in the plot
2. **Indicator_2_commodities**: Presence of commodity crops
3. **Indicator_3_disturbance_before_2020**: Forest disturbance before 2020
4. **Indicator_4_disturbance_after_2020**: Forest disturbance after 2020

### Risk Classification Logic

- **Low**: No tree cover OR commodities present OR disturbance before 2020
- **High**: Tree cover + no commodities + no disturbance before 2020 + disturbance after 2020
- **More info needed**: Tree cover + no commodities + no disturbance (before or after 2020)

## Docker Deployment

### Build and run with Docker Compose:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f
```

### Stop the container:
```bash
docker-compose down
```

## Limitations

- Maximum **500 features** for in-memory processing (configurable)
- Larger datasets will return a message directing to Google Drive export workflow
- Requires active GEE authentication
- Processing time depends on plot size and number

## Troubleshooting

### GEE Authentication Issues

If you see `Failed to initialize Google Earth Engine`:

1. Run `earthengine authenticate` in your terminal
2. Ensure your `GEE_PROJECT` is set correctly in `.env`
3. Check you have access to the GEE project

### Import Errors

If modules can't be found:

1. Ensure you're running from the `api` directory
2. Check that the parent `whisp` directory contains all required modules
3. Verify your `PYTHONPATH` includes the whisp root directory

### Docker Issues

If the Docker container fails to start:

1. Check your `.env` file exists and has valid values
2. Ensure port 8000 is not already in use
3. Review logs: `docker-compose logs`

## Architecture

```
api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration
│   └── models/
│       ├── __init__.py
│       └── schemas.py       # Pydantic models
├── tests/
│   ├── test_api.py          # Automated tests
│   └── example_requests.sh  # Manual test examples
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose config
├── .env.example           # Environment template
├── .gitignore
└── README.md
```

## Related Documentation

- [Whisp Main README](../README.md)
- [Dataset Descriptions](../layers_description.md)
- [Google Earth Engine Docs](https://developers.google.com/earth-engine)

## Support

For issues or questions:
1. Check the [main Whisp documentation](../README.md)
2. Review the interactive API docs at `/docs`
3. Open an issue on the project repository

## License

This API follows the same license as the main Whisp project.

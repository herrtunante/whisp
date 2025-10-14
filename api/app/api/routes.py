"""
API routes for Whisp geospatial analysis
"""
import sys
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import pandas as pd
import ee

# Add parent directory to path to import whisp modules
whisp_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(whisp_root))

from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    ErrorResponse
)
from app.core.config import settings

# Import Whisp modules
try:
    from modules.stats import get_stats
    from modules.risk import whisp_risk
    from modules.utils import collection_properties_to_df
    import geemap
except ImportError as e:
    print(f"Warning: Could not import Whisp modules: {e}")
    print("Make sure the API is run from the correct directory with access to Whisp modules")


router = APIRouter()


def initialize_gee():
    """Initialize Google Earth Engine"""
    try:
        # Try to initialize with project if specified
        if settings.GEE_PROJECT:
            ee.Initialize(project=settings.GEE_PROJECT)
        else:
            ee.Initialize()
        return True
    except Exception as e:
        print(f"Failed to initialize GEE: {e}")
        return False


def geojson_to_ee(geojson_str: str) -> ee.FeatureCollection:
    """Convert GeoJSON string to Earth Engine FeatureCollection"""
    try:
        geojson_dict = json.loads(geojson_str) if isinstance(geojson_str, str) else geojson_str
        return ee.FeatureCollection(geojson_dict)
    except Exception as e:
        raise ValueError(f"Failed to parse GeoJSON: {str(e)}")


def fc_to_dataframe(fc: ee.FeatureCollection, num_features: int) -> pd.DataFrame:
    """Convert FeatureCollection to pandas DataFrame"""
    try:
        if num_features <= 500:
            # For small datasets, use geemap for faster conversion
            df = geemap.ee_to_pandas(fc)
        else:
            # For large datasets, use custom function
            df = collection_properties_to_df(fc)
        return df
    except Exception as e:
        raise ValueError(f"Failed to convert FeatureCollection to DataFrame: {str(e)}")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API is running and GEE is initialized"
)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    gee_status = initialize_gee()

    return HealthResponse(
        status="healthy" if gee_status else "degraded",
        version=settings.API_VERSION,
        gee_initialized=gee_status
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze plots",
    description="Run geospatial analysis on plots using Google Earth Engine datasets",
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def analyze_plots(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze plots for forest and deforestation risk.

    This endpoint:
    1. Accepts either GEE asset paths or GeoJSON input
    2. Runs zonal statistics across 150+ Earth observation datasets
    3. Optionally calculates EUDR risk indicators and classification
    4. Returns results as structured JSON
    """

    try:
        # Initialize GEE
        if not initialize_gee():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize Google Earth Engine. Check authentication."
            )

        # Parse input based on type
        if request.input_type == "gee_asset":
            try:
                feature_collection = ee.FeatureCollection(request.input_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to load GEE asset: {str(e)}"
                )
        elif request.input_type == "geojson":
            try:
                feature_collection = geojson_to_ee(request.input_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to parse GeoJSON: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input_type: {request.input_type}"
            )

        # Get number of features
        try:
            num_features = feature_collection.size().getInfo()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get feature count: {str(e)}"
            )

        if num_features == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input contains no features"
            )

        # Check if dataset is too large
        if num_features > settings.WHISP_THRESHOLD_TO_DRIVE:
            return AnalyzeResponse(
                status="too_large",
                num_features=num_features,
                output_unit=request.output_unit.value,
                risk_calculated=False,
                results=[],
                message=f"Dataset has {num_features} features, which exceeds the limit of {settings.WHISP_THRESHOLD_TO_DRIVE}. "
                        f"Please use the Google Drive export workflow or reduce the number of features."
            )

        # Run Whisp analysis
        try:
            # Temporarily set the output unit in config
            import parameters.config_runtime as config
            original_unit = config.percent_or_ha
            config.percent_or_ha = request.output_unit.value

            # Run stats
            stats_fc = get_stats(feature_collection)

            # Convert to DataFrame
            df = fc_to_dataframe(stats_fc, num_features)

            # Convert numeric columns from strings to floats
            for col in df.columns:
                if col not in ['Plot_ID', 'Geometry_type', 'Country', 'Admin_Level_1',
                               'In_waterbody', 'Unit', 'geoid', 'system:index', 'id', 'name']:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except:
                        pass

            # Restore original unit
            config.percent_or_ha = original_unit

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to run analysis: {str(e)}"
            )

        # Calculate risk if requested
        if request.calculate_risk:
            try:
                df = whisp_risk(
                    df,
                    ind_1_pcent_threshold=request.ind_1_threshold,
                    ind_2_pcent_threshold=request.ind_2_threshold,
                    ind_3_pcent_threshold=request.ind_3_threshold,
                    ind_4_pcent_threshold=request.ind_4_threshold
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to calculate risk: {str(e)}"
                )

        # Convert DataFrame to list of dicts for JSON response
        results = df.to_dict(orient="records")

        return AnalyzeResponse(
            status="success",
            num_features=num_features,
            output_unit=request.output_unit.value,
            risk_calculated=request.calculate_risk,
            results=results,
            message=f"Successfully analyzed {num_features} features"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/",
    summary="API root",
    description="Get basic API information"
)
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs": "/docs",
        "health": "/health"
    }

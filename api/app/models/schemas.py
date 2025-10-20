"""
Pydantic models for request and response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum


class InputType(str, Enum):
    """Type of input geometry"""
    GEE_ASSET = "gee_asset"
    GEOJSON = "geojson"


class OutputUnit(str, Enum):
    """Unit for statistics output"""
    HECTARES = "ha"
    PERCENT = "percent"


class RiskLevel(str, Enum):
    """EUDR risk levels"""
    LOW = "low"
    HIGH = "high"
    MORE_INFO_NEEDED = "more_info_needed"


class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint"""
    input_type: InputType = Field(
        ...,
        description="Type of input: 'gee_asset' for Earth Engine asset path, or 'geojson' for GeoJSON"
    )
    input_data: str = Field(
        ...,
        description="GEE asset path (e.g., 'projects/ee-whisp/assets/example') or GeoJSON string"
    )
    output_unit: OutputUnit = Field(
        default=OutputUnit.HECTARES,
        description="Output unit: 'ha' for hectares or 'percent' for percentage"
    )
    calculate_risk: bool = Field(
        default=False,
        description="Whether to calculate EUDR risk indicators and classification"
    )
    ind_1_threshold: float = Field(
        default=10.0,
        ge=0,
        le=100,
        description="Threshold for Indicator 1 (treecover) in percent"
    )
    ind_2_threshold: float = Field(
        default=10.0,
        ge=0,
        le=100,
        description="Threshold for Indicator 2 (commodities) in percent"
    )
    ind_3_threshold: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Threshold for Indicator 3 (disturbance before 2020) in percent"
    )
    ind_4_threshold: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Threshold for Indicator 4 (disturbance after 2020) in percent"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "input_type": "gee_asset",
                "input_data": "projects/ee-whisp/assets/example_plots",
                "output_unit": "ha",
                "calculate_risk": True,
                "ind_1_threshold": 10.0,
                "ind_2_threshold": 10.0,
                "ind_3_threshold": 0.0,
                "ind_4_threshold": 0.0
            }
        }


class PlotStatistics(BaseModel):
    """Statistics for a single plot"""
    plot_id: Optional[str] = None
    plot_area_ha: Optional[float] = None
    geometry_type: Optional[str] = None
    country: Optional[str] = None
    admin_level_1: Optional[str] = None
    centroid_lon: Optional[float] = None
    centroid_lat: Optional[float] = None
    in_waterbody: Optional[str] = None
    unit: Optional[str] = None
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dataset statistics as key-value pairs"
    )

    # Risk indicators (if calculated)
    indicator_1_treecover: Optional[str] = None
    indicator_2_commodities: Optional[str] = None
    indicator_3_disturbance_before_2020: Optional[str] = None
    indicator_4_disturbance_after_2020: Optional[str] = None
    eudr_risk: Optional[RiskLevel] = None


class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint"""
    status: str = Field(..., description="Status of the analysis")
    num_features: int = Field(..., description="Number of features analyzed")
    output_unit: str = Field(..., description="Unit used for statistics")
    risk_calculated: bool = Field(..., description="Whether risk was calculated")
    results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Analysis results for each plot"
    )
    message: Optional[str] = Field(
        None,
        description="Additional information or warnings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "num_features": 10,
                "output_unit": "ha",
                "risk_calculated": True,
                "results": [
                    {
                        "Plot_ID": 1,
                        "Plot_area_ha": 25.5,
                        "Country": "Brazil",
                        "EUDR_risk": "low"
                    }
                ],
                "message": "Analysis completed successfully"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version")
    gee_initialized: bool = Field(..., description="Whether Google Earth Engine is initialized")


class ErrorResponse(BaseModel):
    """Response model for errors"""
    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Type of error")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Failed to process GEE asset",
                "error_type": "GEEError"
            }
        }

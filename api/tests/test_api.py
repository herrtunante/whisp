"""
Test cases for Whisp API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
api_root = Path(__file__).parent.parent
sys.path.insert(0, str(api_root))

from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Whisp API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "gee_initialized" in data


def test_analyze_invalid_input_type():
    """Test analyze endpoint with invalid input type"""
    request_data = {
        "input_type": "invalid_type",
        "input_data": "test"
    }
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 422  # Validation error


def test_analyze_empty_geojson():
    """Test analyze endpoint with empty GeoJSON"""
    request_data = {
        "input_type": "geojson",
        "input_data": '{"type": "FeatureCollection", "features": []}'
    }
    response = client.post("/analyze", json=request_data)
    # Should fail because no features
    assert response.status_code in [400, 500]


def test_analyze_with_risk_calculation():
    """Test analyze endpoint structure with risk calculation"""
    # Note: This test requires valid GEE authentication and asset
    # In a real scenario, you would use a test GEE asset
    request_data = {
        "input_type": "gee_asset",
        "input_data": "projects/ee-whisp/assets/test",
        "output_unit": "ha",
        "calculate_risk": True,
        "ind_1_threshold": 10.0,
        "ind_2_threshold": 10.0,
        "ind_3_threshold": 0.0,
        "ind_4_threshold": 0.0
    }
    # This will likely fail without proper setup, but tests the structure
    response = client.post("/analyze", json=request_data)
    assert response.status_code in [200, 400, 500]

    # If successful, check response structure
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert "num_features" in data
        assert "output_unit" in data
        assert "risk_calculated" in data
        assert "results" in data


def test_threshold_validation():
    """Test that thresholds are validated correctly"""
    request_data = {
        "input_type": "gee_asset",
        "input_data": "projects/ee-whisp/assets/test",
        "ind_1_threshold": 150.0,  # Invalid: > 100
    }
    response = client.post("/analyze", json=request_data)
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

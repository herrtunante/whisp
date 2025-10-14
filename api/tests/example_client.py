"""
Example Python client for testing Whisp API
"""
import requests
import json
from typing import Dict, Any


class WhispAPIClient:
    """Simple client for interacting with Whisp API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def analyze_gee_asset(
        self,
        asset_path: str,
        output_unit: str = "ha",
        calculate_risk: bool = True,
        ind_1_threshold: float = 10.0,
        ind_2_threshold: float = 10.0,
        ind_3_threshold: float = 0.0,
        ind_4_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Analyze a GEE asset

        Args:
            asset_path: Path to GEE asset (e.g., "projects/ee-whisp/assets/my_plots")
            output_unit: "ha" or "percent"
            calculate_risk: Whether to calculate EUDR risk
            ind_1_threshold: Threshold for indicator 1 (treecover)
            ind_2_threshold: Threshold for indicator 2 (commodities)
            ind_3_threshold: Threshold for indicator 3 (disturbance before 2020)
            ind_4_threshold: Threshold for indicator 4 (disturbance after 2020)

        Returns:
            API response as dictionary
        """
        payload = {
            "input_type": "gee_asset",
            "input_data": asset_path,
            "output_unit": output_unit,
            "calculate_risk": calculate_risk,
            "ind_1_threshold": ind_1_threshold,
            "ind_2_threshold": ind_2_threshold,
            "ind_3_threshold": ind_3_threshold,
            "ind_4_threshold": ind_4_threshold
        }

        response = requests.post(f"{self.base_url}/analyze", json=payload)
        response.raise_for_status()
        return response.json()

    def analyze_geojson(
        self,
        geojson: Dict[str, Any] or str,
        output_unit: str = "ha",
        calculate_risk: bool = True,
        ind_1_threshold: float = 10.0,
        ind_2_threshold: float = 10.0,
        ind_3_threshold: float = 0.0,
        ind_4_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Analyze GeoJSON data

        Args:
            geojson: GeoJSON dict or string
            output_unit: "ha" or "percent"
            calculate_risk: Whether to calculate EUDR risk
            ind_1_threshold: Threshold for indicator 1
            ind_2_threshold: Threshold for indicator 2
            ind_3_threshold: Threshold for indicator 3
            ind_4_threshold: Threshold for indicator 4

        Returns:
            API response as dictionary
        """
        # Convert dict to string if needed
        if isinstance(geojson, dict):
            geojson_str = json.dumps(geojson)
        else:
            geojson_str = geojson

        payload = {
            "input_type": "geojson",
            "input_data": geojson_str,
            "output_unit": output_unit,
            "calculate_risk": calculate_risk,
            "ind_1_threshold": ind_1_threshold,
            "ind_2_threshold": ind_2_threshold,
            "ind_3_threshold": ind_3_threshold,
            "ind_4_threshold": ind_4_threshold
        }

        response = requests.post(f"{self.base_url}/analyze", json=payload)
        response.raise_for_status()
        return response.json()


def example_usage():
    """Example usage of the Whisp API client"""

    # Initialize client
    client = WhispAPIClient("http://localhost:8000")

    print("=" * 60)
    print("Whisp API Client Examples")
    print("=" * 60)

    # 1. Health check
    print("\n1. Health Check")
    print("-" * 60)
    try:
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Version: {health['version']}")
        print(f"GEE Initialized: {health['gee_initialized']}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Analyze GEE asset
    print("\n2. Analyze GEE Asset")
    print("-" * 60)
    try:
        result = client.analyze_gee_asset(
            asset_path="projects/ee-whisp/assets/example_plots",
            output_unit="ha",
            calculate_risk=True,
            ind_1_threshold=10.0,
            ind_2_threshold=10.0,
            ind_3_threshold=0.0,
            ind_4_threshold=0.0
        )
        print(f"Status: {result['status']}")
        print(f"Number of features: {result['num_features']}")
        print(f"Risk calculated: {result['risk_calculated']}")
        print(f"Message: {result['message']}")

        if result['results']:
            print(f"\nFirst result:")
            first = result['results'][0]
            print(f"  Plot ID: {first.get('Plot_ID', 'N/A')}")
            print(f"  Area: {first.get('Plot_area_ha', 'N/A')} ha")
            print(f"  Country: {first.get('Country', 'N/A')}")
            if result['risk_calculated']:
                print(f"  EUDR Risk: {first.get('EUDR_risk', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Analyze GeoJSON
    print("\n3. Analyze GeoJSON")
    print("-" * 60)
    try:
        # Example polygon in Brazil
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-51.0, -10.0],
                                [-51.0, -10.1],
                                [-50.9, -10.1],
                                [-50.9, -10.0],
                                [-51.0, -10.0]
                            ]
                        ]
                    },
                    "properties": {
                        "id": 1,
                        "name": "Test Plot"
                    }
                }
            ]
        }

        result = client.analyze_geojson(
            geojson=geojson,
            output_unit="percent",
            calculate_risk=True
        )
        print(f"Status: {result['status']}")
        print(f"Number of features: {result['num_features']}")
        print(f"Output unit: {result['output_unit']}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    example_usage()

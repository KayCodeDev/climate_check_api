from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from main import app
from models import AirQualityData

client = TestClient(app)

@pytest.fixture
def mock_fetch_air_quality():
    """Mock the fetch_air_quality_data function"""
    sample_data = {
        "indexes": [
            {
                "code": "us-epa-index",
                "aqi": 42,
                "category": "Good",
                "dominantPollutant": "pm25"
            }
        ],
        "pollutants": {
            "pm25": {
                "concentration": {
                    "value": 10.2,
                    "units": "µg/m³"
                },
                "category": "Good"
            }
        },
        "healthRecommendations": {}
    }
    
    with patch("functions.google_services.fetch_air_quality_data", 
               new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = sample_data
        yield mock_fetch

@pytest.fixture
def mock_claude_analysis():
    """Mock the get_claude_analysis function"""
    sample_analysis = {
        "daily_activity_impact": "Good for all activities",
        "health_implications": {
            "general_population": "No issues expected"
        },
        "pollutant_sources": "Traffic and industry",
        "indoor_recommendations": "Normal ventilation",
        "long_term_concerns": "None at this level"
    }
    
    with patch("functions.ai_services.get_claude_analysis", 
               new_callable=AsyncMock) as mock_analysis:
        mock_analysis.return_value = sample_analysis
        yield mock_analysis

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome" in response.json()["message"]

def test_air_quality_endpoint(mock_fetch_air_quality, mock_claude_analysis):
    """Test the air quality analysis endpoint"""
    response = client.get("/air-quality/?latitude=37.7749&longitude=-122.4194&location_name=San%20Francisco")
    
    assert response.status_code == 200
    assert "raw_data" in response.json()
    assert "location" in response.json()
    assert "claude_analysis" in response.json()
    
    assert response.json()["location"] == "San Francisco"
    assert response.json()["raw_data"]["aqi"] == 42
    assert response.json()["raw_data"]["category"] == "Good"
    assert "daily_activity_impact" in response.json()["claude_analysis"]
    
    mock_fetch_air_quality.assert_called_once()
    mock_claude_analysis.assert_called_once()

def test_air_quality_missing_params():
    """Test the air quality endpoint with missing parameters"""
    response = client.get("/air-quality/?latitude=37.7749")
    assert response.status_code == 422  # Unprocessable Entity for missing required parameters
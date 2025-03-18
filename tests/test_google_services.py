import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from fastapi import HTTPException

from functions.google_services import fetch_air_quality_data, process_air_quality_data
from models import AirQualityData

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Setup mock environment variables for testing"""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_api_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_api_key")

@pytest.fixture
def sample_raw_aqi_data():
    """Sample raw AQI data for testing"""
    return {
        "indexes": [
            {
                "code": "us-epa-index",
                "displayName": "US EPA Index",
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
            },
            "pm10": {
                "concentration": {
                    "value": 18.7,
                    "units": "µg/m³"
                },
                "category": "Good"
            }
        },
        "healthRecommendations": {
            "generalPopulation": "Air quality is acceptable.",
            "sensitiveGroups": "Unusually sensitive individuals may experience respiratory symptoms."
        }
    }

@pytest.mark.asyncio
async def test_fetch_air_quality_data_success(mock_env_vars, sample_raw_aqi_data):
    """Test successful fetch of air quality data"""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = sample_raw_aqi_data
        mock_post.return_value = mock_response

        result = await fetch_air_quality_data(37.7749, -122.4194)
        
        assert result == sample_raw_aqi_data
        mock_post.assert_called_once()
        url_called = mock_post.call_args[0][0]
        assert "airquality.googleapis.com" in url_called

@pytest.mark.asyncio
async def test_fetch_air_quality_data_api_error(mock_env_vars):
    """Test handling of API errors when fetching air quality data"""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_error = httpx.HTTPError("API Error")
        mock_error.response = MagicMock()
        mock_error.response.status_code = 403
        mock_post.side_effect = mock_error

        with pytest.raises(HTTPException) as excinfo:
            await fetch_air_quality_data(37.7749, -122.4194)
        
        assert excinfo.value.status_code == 403
        assert "Google API error" in str(excinfo.value.detail)

def test_process_air_quality_data_success(sample_raw_aqi_data):
    """Test successful processing of air quality data"""
    result = process_air_quality_data(sample_raw_aqi_data)
    
    assert isinstance(result, AirQualityData)
    assert result.aqi == 42
    assert result.category == "Good"
    assert result.dominant_pollutant == "pm25"
    assert "pm25" in result.pollutants
    assert result.pollutants["pm25"]["concentration"] == 10.2
    assert "generalPopulation" in result.health_recommendations

def test_process_air_quality_data_invalid():
    """Test handling of invalid air quality data"""
    with pytest.raises(HTTPException) as excinfo:
        process_air_quality_data({})
    
    assert excinfo.value.status_code == 400
    assert "Invalid or empty air quality data" in str(excinfo.value.detail)

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from functions.ai_services import get_claude_analysis
from models import AirQualityData

@pytest.fixture
def sample_aqi_data():
    """Sample processed AQI data for testing"""
    return AirQualityData(
        aqi=42,
        category="Good",
        dominant_pollutant="pm25",
        pollutants={
            "pm25": {
                "concentration": 10.2,
                "unit": "µg/m³",
                "category": "Good"
            }
        },
        health_recommendations={
            "generalPopulation": "Air quality is acceptable."
        }
    )

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Setup mock environment variables for testing"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_api_key")

@pytest.mark.asyncio
async def test_claude_analysis_success(mock_env_vars, sample_aqi_data):
    """Test successful Claude analysis"""
    sample_claude_response = MagicMock()
    sample_claude_response.content = [MagicMock()]
    sample_claude_response.content[0].text = """```json
{
  "daily_activity_impact": "The air quality is good and suitable for all activities.",
  "health_implications": {
    "general_population": "No health impacts expected.",
    "sensitive_groups": "Very minimal risk.",
    "children": "Safe for outdoor play.",
    "elderly": "Safe for normal activities."
  },
  "pollutant_sources": "PM2.5 typically comes from combustion sources like vehicles and industrial processes.",
  "indoor_recommendations": "Standard ventilation is fine.",
  "long_term_concerns": "None at this level."
}
```"""

    with patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = sample_claude_response
        MockAnthropic.return_value = mock_client
        
        result = await get_claude_analysis(sample_aqi_data, "San Francisco")
        
        assert "daily_activity_impact" in result
        assert "health_implications" in result
        assert "pollutant_sources" in result
        assert result["daily_activity_impact"] == "The air quality is good and suitable for all activities."
        MockAnthropic.assert_called_once_with(api_key="test_anthropic_api_key")

@pytest.mark.asyncio
async def test_claude_analysis_no_api_key(monkeypatch, sample_aqi_data):
    """Test Claude analysis with missing API key"""
    # Ensure the API key is not set
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    
    result = await get_claude_analysis(sample_aqi_data, "San Francisco")
    
    assert "error" in result
    assert "API key not configured" in result["error"]

@pytest.mark.asyncio
async def test_claude_analysis_exception(mock_env_vars, sample_aqi_data):
    """Test handling of exceptions in Claude analysis"""
    with patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API error")
        MockAnthropic.return_value = mock_client
        
        result = await get_claude_analysis(sample_aqi_data, "San Francisco")
        
        assert "error" in result
        assert "Failed to get Claude analysis" in result["error"]
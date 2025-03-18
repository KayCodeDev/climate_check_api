from pydantic import BaseModel


class AirQualityData(BaseModel):
    aqi: float
    category: str
    dominant_pollutant: str
    pollutants: dict
    health_recommendations: dict

class AirQualityAnalysis(BaseModel):
    raw_data: AirQualityData
    location: str
    analysis: dict
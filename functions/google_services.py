import os
from fastapi import HTTPException
import httpx

from models import AirQualityData

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


async def fetch_air_quality_data(latitude: float, longitude: float):
    url = "https://airquality.googleapis.com/v1/currentConditions:lookup"
    params = {
        "key": GOOGLE_API_KEY,
    }
    
    payload = {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Google API error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
        
        
# Helper function to process air quality data
def process_air_quality_data(data):
    if not data or "indexes" not in data:
        raise HTTPException(status_code=400, detail="Invalid or empty air quality data")
    
    indexes = data.get("indexes", [])
    pollutants = data.get("pollutants", {})
    
    # Find the main AQI (typically the first index, which is usually the US EPA standard)
    main_aqi = next((index for index in indexes if index.get("code") == "us-epa-index"), indexes[0])
    
    # Process pollutants data
    processed_pollutants = {}
    for pollutant_name, pollutant_data in pollutants.items():
        concentration = pollutant_data.get("concentration", {})
        processed_pollutants[pollutant_name] = {
            "concentration": concentration.get("value", 0),
            "unit": concentration.get("units", ""),
            "category": pollutant_data.get("category", ""),
        }
    
    # Process health recommendations
    health_recommendations = data.get("healthRecommendations", {})
    
    return AirQualityData(
        aqi=main_aqi.get("aqi", 0),
        category=main_aqi.get("category", ""),
        dominant_pollutant=main_aqi.get("dominantPollutant", ""),
        pollutants=processed_pollutants,
        health_recommendations=health_recommendations
    )
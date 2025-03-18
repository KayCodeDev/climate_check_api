import os
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

from functions.ai_services import get_claude_analysis
from functions.google_services import fetch_air_quality_data, process_air_quality_data
from models import AirQualityAnalysis, AirQualityData

# Load environment variables
load_dotenv()

# Check if required API keys are set
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY not set in environment variables")
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Warning: ANTHROPIC_API_KEY not set in environment variables")

# Initialize FastAPI app
app = FastAPI(
    title="Air Quality Analysis API",
    description="An API that combines Google Air Quality data with Claude AI insights",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Air Quality Analysis API. Use /air-quality endpoint for analysis. by Kenneth I"}

@app.get("/air-quality/", response_model=AirQualityAnalysis)
async def get_air_quality_analysis(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
    location_name: str = Query(..., description="Name of the location for reference")
):
    # Fetch air quality data from Google
    raw_data = await fetch_air_quality_data(latitude, longitude)
    
    # Process the raw data
    processed_data = process_air_quality_data(raw_data)
    
    # Get Claude analysis
    claude_analysis = await get_claude_analysis(processed_data, location_name)
    
    # Return combined results
    return AirQualityAnalysis(
        raw_data=processed_data,
        location=location_name,
        claude_analysis=claude_analysis
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
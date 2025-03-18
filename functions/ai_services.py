
import os
import json
import re

from anthropic import Anthropic
from models import AirQualityData

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

async def get_claude_analysis(air_quality_data: AirQualityData, location: str):
    prompt = f"""
    I need a detailed analysis of the following air quality data for {location}:
    
    AQI: {air_quality_data.aqi}
    Category: {air_quality_data.category}
    Dominant Pollutant: {air_quality_data.dominant_pollutant}
    
    Pollutants:
    {air_quality_data.pollutants}
    
    Health Recommendations:
    {air_quality_data.health_recommendations}
    
    Please provide:
    1. A simplified explanation of what this AQI means for daily activities
    2. Health implications for different groups (general population, sensitive groups, children, elderly)
    3. Likely sources of the dominant pollutant in this area
    4. Recommendations for improving indoor air quality given these conditions
    5. Long-term health concerns if this air quality persists
    
    Format your response as a structured JSON object with these sections.
    """
    
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        
        # Try to find and parse JSON from the response
        response_text = response.content[0].text
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON code block found, try to parse the whole response
            json_str = response_text
            
        try:
            analysis = json.loads(json_str)
        except json.JSONDecodeError:
            # If parsing fails, return the text as a simple analysis
            analysis = {"raw_analysis": response_text}
            
        return analysis
    
    except Exception as e:
        return {"error": f"Failed to get Claude analysis: {str(e)}"}

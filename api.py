"""API interaction module for weather data."""

import httpx
from typing import Dict, Any
from config import OPENWEATHER_API_BASE, OPENWEATHER_API_KEY, USER_AGENT

async def make_weather_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to the OpenWeatherMap API with proper error handling.
    
    Args:
        endpoint: API endpoint (e.g., "weather", "forecast")
        params: Query parameters for the request
        
    Returns:
        JSON response or error dictionary
    """
    params["appid"] = OPENWEATHER_API_KEY
    params["units"] = "metric"  # Use Celsius
    params["lang"] = "tr"  # Turkish language for descriptions
    
    url = f"{OPENWEATHER_API_BASE}/{endpoint}"
    headers = {"User-Agent": USER_AGENT}
    
    # Check if using placeholder API key
    if OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {
            "error": "Demo mode: Please replace 'YOUR_API_KEY_HERE' with a valid OpenWeatherMap API key."
        }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"Request error: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

async def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Get current weather for a specific location.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Current weather data
    """
    return await make_weather_request("weather", {"lat": lat, "lon": lon})

async def get_weather_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather forecast for a specific location.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Forecast weather data
    """
    return await make_weather_request("forecast", {"lat": lat, "lon": lon})

async def get_air_quality(lat: float, lon: float) -> Dict[str, Any]:
    """Get air quality data for a specific location.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Air quality data
    """
    return await make_weather_request("air_pollution", {"lat": lat, "lon": lon})

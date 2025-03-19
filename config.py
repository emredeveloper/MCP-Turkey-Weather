"""Configuration settings and constants for the weather application."""

# API Configuration
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_API_KEY = "your_key"
USER_AGENT = "weather-turkey-app/1.0"

# Dictionary of major Turkish cities with their coordinates
TURKISH_CITIES = {
    "istanbul": {"lat": 41.0082, "lon": 28.9784, "name": "İstanbul"},
    "ankara": {"lat": 39.9334, "lon": 32.8597, "name": "Ankara"},
    "izmir": {"lat": 38.4237, "lon": 27.1428, "name": "İzmir"},
    "antalya": {"lat": 36.8841, "lon": 30.7056, "name": "Antalya"},
    "bursa": {"lat": 40.1885, "lon": 29.0610, "name": "Bursa"},
    "adana": {"lat": 37.0000, "lon": 35.3213, "name": "Adana"},
    "konya": {"lat": 37.8667, "lon": 32.4833, "name": "Konya"},
    "gaziantep": {"lat": 37.0662, "lon": 37.3833, "name": "Gaziantep"},
    "mersin": {"lat": 36.8000, "lon": 34.6333, "name": "Mersin"},
    "diyarbakir": {"lat": 37.9144, "lon": 40.2306, "name": "Diyarbakır"},
    "kayseri": {"lat": 38.7312, "lon": 35.4787, "name": "Kayseri"}
}

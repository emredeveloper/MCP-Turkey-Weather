"""Main module for the weather application with MCP tools."""

from typing import Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Import from our modules
from config import TURKISH_CITIES
from utils import (normalize_turkish_text, get_weather_emoji, get_turkish_day_name, 
                  get_aqi_recommendations, compare_values, generate_demo_weather,
                  generate_demo_hourly_forecast, generate_demo_air_quality,
                  generate_demo_city_comparison, generate_demo_activity_recommendations)
from api import make_weather_request, get_current_weather, get_weather_forecast, get_air_quality

# Initialize FastMCP server
mcp = FastMCP("weather-turkey")

@mcp.tool()
async def hava_durumu(enlem: float, boylam: float, yer_adi: Optional[str] = None) -> str:
    """Belirli bir konum için hava durumu tahminini alır.

    Args:
        enlem: Konumun enlemi
        boylam: Konumun boylamı
        yer_adi: Konumun adı (opsiyonel)
    """
    # Validate parameters
    if not (-90 <= enlem <= 90):
        return "Geçersiz enlem değeri. Enlem -90 ile 90 arasında olmalıdır."
        
    if not (-180 <= boylam <= 180):
        return "Geçersiz boylam değeri. Boylam -180 ile 180 arasında olmalıdır."
    
    weather_data = await get_current_weather(enlem, boylam)
    
    if "error" in weather_data:
        if "Demo mode" in weather_data["error"]:
            # Generate demo data if using placeholder API key
            return generate_demo_weather(enlem, boylam, yer_adi, TURKISH_CITIES)
        return f"Hava durumu bilgisi alınamadı: {weather_data['error']}"
    
    forecast_data = await get_weather_forecast(enlem, boylam)
    if "error" in forecast_data:
        return f"Hava durumu tahmini alınamadı: {forecast_data['error']}"
    
    location = yer_adi or f"{weather_data.get('name', 'Bilinmeyen Konum')}"
    
    # Current weather
    current = weather_data
    current_temp = current.get("main", {}).get("temp", "N/A")
    current_feels = current.get("main", {}).get("feels_like", "N/A")
    current_humidity = current.get("main", {}).get("humidity", "N/A")
    current_description = current.get("weather", [{}])[0].get("description", "N/A")
    
    # Wind information
    wind_speed = current.get("wind", {}).get("speed", "N/A")
    wind_direction = current.get("wind", {}).get("deg", "N/A")
    
    # Format wind direction
    directions = ["kuzey", "kuzeydoğu", "doğu", "güneydoğu", "güney", "güneybatı", "batı", "kuzeybatı"]
    wind_dir_text = directions[round(((wind_direction % 360) / 45) % 8)] if isinstance(wind_direction, (int, float)) else "N/A"
    
    # Build current weather report
    result = f"""🌤️ HAVA DURUMU: {location.upper()} 🌤️

MEVCUT DURUM:
🌡️ Sıcaklık: {current_temp}°C (Hissedilen: {current_feels}°C)
💧 Nem: %{current_humidity}
🌬️ Rüzgar: {wind_speed} m/s, yönü {wind_dir_text}
🔍 Durum: {current_description}

5 GÜNLÜK TAHMİN:
"""
    
    # Extract forecast for next 5 days (every 24 hours)
    forecast_items = forecast_data.get("list", [])
    seen_dates = set()
    daily_forecasts = []
    
    for item in forecast_items:
        dt = datetime.fromtimestamp(item["dt"])
        date_str = dt.strftime("%Y-%m-%d")
        
        if date_str in seen_dates:
            continue
            
        seen_dates.add(date_str)
        if len(seen_dates) > 5:
            break
            
        temp = item["main"]["temp"]
        condition = item["weather"][0]["description"]
        
        daily_forecasts.append(f"{dt.strftime('%d.%m.%Y')} - {temp}°C, {condition}")
    
    result += "\n".join(daily_forecasts)
    return result

@mcp.tool()
async def hava_durumu_sehir(sehir: str) -> str:
    """Türkiye'deki bir şehir için hava durumu tahminini alır.

    Args:
        sehir: Türkiye'deki şehir adı (örn. İstanbul, Ankara)
    """
    normalized_input = normalize_turkish_text(sehir)
    
    if normalized_input not in TURKISH_CITIES:
        close_matches = [city for city in TURKISH_CITIES if normalized_input in normalize_turkish_text(city)]
        
        if close_matches:
            suggested = ", ".join([TURKISH_CITIES[city]["name"] for city in close_matches])
            return f"'{sehir}' bulunamadı. Bunlardan birini mi demek istediniz? {suggested}"
        
        return f"'{sehir}' için hava durumu bilgisi bulunamadı. Lütfen geçerli bir Türk şehri adı girin."
    
    city_data = TURKISH_CITIES[normalized_input]
    return await hava_durumu(city_data["lat"], city_data["lon"], city_data["name"])

@mcp.tool()
async def saatlik_hava_durumu(sehir: str, gun_sayisi: int = 1) -> str:
    """Belirli bir şehir için saatlik hava durumu tahminlerini alır.
    
    Args:
        sehir: Türkiye'deki şehir adı (örn. İstanbul, Ankara)
        gun_sayisi: Kaç günlük tahmin isteniyor (1-5 arası, varsayılan 1)
    """
    # Validate days parameter
    if not (1 <= gun_sayisi <= 5):
        return "Geçersiz gün sayısı. Değer 1-5 arasında olmalıdır."
    
    # Normalize city name and get coordinates
    normalized_input = normalize_turkish_text(sehir)
    if normalized_input not in TURKISH_CITIES:
        return f"'{sehir}' için hava durumu bilgisi bulunamadı. Lütfen geçerli bir Türk şehri adı girin."
    
    city_data = TURKISH_CITIES[normalized_input]
    lat, lon = city_data["lat"], city_data["lon"]
    
    # Get hourly forecast data
    forecast_data = await make_weather_request("forecast", {"lat": lat, "lon": lon})
    
    if "error" in forecast_data:
        if "Demo mode" in forecast_data["error"]:
            return generate_demo_hourly_forecast(city_data["name"], gun_sayisi)
        return f"Hava durumu tahmini alınamadı: {forecast_data['error']}"
    
    # Format hourly data
    result = f"🕒 {city_data['name']} İÇİN SAATLİK HAVA DURUMU 🕒\n\n"
    
    forecast_items = forecast_data.get("list", [])
    hours_to_show = min(gun_sayisi * 24, len(forecast_items))
    
    current_date = None
    for i in range(min(hours_to_show, len(forecast_items))):
        item = forecast_items[i]
        dt = datetime.fromtimestamp(item["dt"])
        
        # Show date at the beginning of a new day
        if current_date != dt.date():
            current_date = dt.date()
            result += f"\n📅 {dt.strftime('%d.%m.%Y')} ({get_turkish_day_name(dt.weekday())})\n"
            
        temp = item["main"]["temp"]
        condition = item["weather"][0]["description"]
        humidity = item["main"]["humidity"]
        wind_speed = item["wind"]["speed"]
        
        # Emoji selection
        emoji = get_weather_emoji(condition)
        
        result += f"{dt.strftime('%H:%M')} - {emoji} {temp}°C, {condition}, Nem: %{humidity}, Rüzgar: {wind_speed}m/s\n"
    
    return result

@mcp.tool()
async def hava_kalitesi(sehir: str) -> str:
    """Belirli bir şehir için hava kalitesi endeksi bilgisini alır.
    
    Args:
        sehir: Türkiye'deki şehir adı (örn. İstanbul, Ankara)
    """
    # Normalize city name and get coordinates
    normalized_input = normalize_turkish_text(sehir)
    if normalized_input not in TURKISH_CITIES:
        return f"'{sehir}' için hava kalitesi bilgisi bulunamadı. Lütfen geçerli bir Türk şehri adı girin."
    
    city_data = TURKISH_CITIES[normalized_input]
    lat, lon = city_data["lat"], city_data["lon"]
    
    # Use the air quality endpoint
    air_quality_data = await get_air_quality(lat, lon)
    
    if "error" in air_quality_data:
        if "Demo mode" in air_quality_data["error"]:
            return generate_demo_air_quality(city_data["name"])
        return f"Hava kalitesi bilgisi alınamadı: {air_quality_data['error']}"
    
    try:
        aqi_data = air_quality_data.get("list", [{}])[0]
        aqi = aqi_data.get("main", {}).get("aqi", 0)
        components = aqi_data.get("components", {})
        
        # Interpret AQI value
        aqi_descriptions = [
            "Bilgi yok",
            "İyi", 
            "Makul", 
            "Hassas gruplar için sağlıksız", 
            "Sağlıksız", 
            "Çok sağlıksız",
            "Tehlikeli"
        ]
        
        aqi_description = aqi_descriptions[min(aqi, len(aqi_descriptions)-1)]
        
        result = f"""🌬️ {city_data['name']} HAVA KALİTESİ 🌬️

Hava Kalitesi Endeksi (AQI): {aqi} - {aqi_description}

🔍 KİRLETİCİLER:
• Partiküller (PM2.5): {components.get('pm2_5', 'N/A')} μg/m³
• Partiküller (PM10): {components.get('pm10', 'N/A')} μg/m³
• Ozon (O₃): {components.get('o3', 'N/A')} μg/m³
• Nitrojen dioksit (NO₂): {components.get('no2', 'N/A')} μg/m³
• Kükürt dioksit (SO₂): {components.get('so2', 'N/A')} μg/m³
• Karbon monoksit (CO): {components.get('co', 'N/A')} μg/m³

💡 TAVSİYELER:
{get_aqi_recommendations(aqi)}
"""
        return result
    except Exception as e:
        return f"Hava kalitesi verileri işlenirken bir hata oluştu: {str(e)}"

@mcp.tool()
async def sehirler_karsilastir(sehir1: str, sehir2: str) -> str:
    """İki farklı şehrin hava durumunu karşılaştırır.
    
    Args:
        sehir1: İlk şehrin adı
        sehir2: İkinci şehrin adı
    """
    # Normalize city names
    normalized_input1 = normalize_turkish_text(sehir1)
    normalized_input2 = normalize_turkish_text(sehir2)
    
    # Check if both cities are in the list
    if normalized_input1 not in TURKISH_CITIES:
        return f"'{sehir1}' için hava durumu bilgisi bulunamadı. Lütfen geçerli bir Türk şehri adı girin."
    
    if normalized_input2 not in TURKISH_CITIES:
        return f"'{sehir2}' için hava durumu bilgisi bulunamadı. Lütfen geçerli bir Türk şehri adı girin."
    
    # Get weather data for both cities
    city_data1 = TURKISH_CITIES[normalized_input1]
    city_data2 = TURKISH_CITIES[normalized_input2]
    
    weather_data1 = await get_current_weather(city_data1["lat"], city_data1["lon"])
    weather_data2 = await get_current_weather(city_data2["lat"], city_data2["lon"])
    
    if "error" in weather_data1 or "error" in weather_data2:
        if "Demo mode" in weather_data1.get("error", "") or "Demo mode" in weather_data2.get("error", ""):
            return generate_demo_city_comparison(city_data1["name"], city_data2["name"])
        
        errors = []
        if "error" in weather_data1:
            errors.append(f"{city_data1['name']}: {weather_data1['error']}")
        if "error" in weather_data2:
            errors.append(f"{city_data2['name']}: {weather_data2['error']}")
        
        return f"Hava durumu karşılaştırması yapılamadı: {', '.join(errors)}"
    
    # Extract and compare data
    temp1 = weather_data1.get("main", {}).get("temp", "N/A")
    temp2 = weather_data2.get("main", {}).get("temp", "N/A")
    
    feels1 = weather_data1.get("main", {}).get("feels_like", "N/A")
    feels2 = weather_data2.get("main", {}).get("feels_like", "N/A")
    
    humidity1 = weather_data1.get("main", {}).get("humidity", "N/A")
    humidity2 = weather_data2.get("main", {}).get("humidity", "N/A")
    
    condition1 = weather_data1.get("weather", [{}])[0].get("description", "N/A")
    condition2 = weather_data2.get("weather", [{}])[0].get("description", "N/A")
    
    wind1 = weather_data1.get("wind", {}).get("speed", "N/A")
    wind2 = weather_data2.get("wind", {}).get("speed", "N/A")
    
    # Comparison texts
    temp_compare = compare_values(temp1, temp2, "daha sıcak", "daha soğuk")
    humidity_compare = compare_values(humidity1, humidity2, "daha nemli", "daha kuru")
    wind_compare = compare_values(wind1, wind2, "daha rüzgarlı", "daha sakin")
    
    result = f"""🔄 HAVA DURUMU KARŞILAŞTIRMASI 🔄

┌─────────────────────┬────────────────┬────────────────┐
│                     │ {city_data1['name']:<14} │ {city_data2['name']:<14} │
├─────────────────────┼────────────────┼────────────────┤
│ Sıcaklık            │ {temp1}°C          │ {temp2}°C          │
│ Hissedilen          │ {feels1}°C          │ {feels2}°C          │
│ Nem                 │ %{humidity1:<13} │ %{humidity2:<13} │
│ Rüzgar              │ {wind1} m/s         │ {wind2} m/s         │
│ Durum               │ {condition1:<14} │ {condition2:<14} │
└─────────────────────┴────────────────┴────────────────┘

📊 KARŞILAŞTIRMA:
• {city_data1['name']}, {city_data2['name']}'dan {temp_compare}.
• {city_data1['name']}, {city_data2['name']}'dan {humidity_compare}.
• {city_data1['name']}, {city_data2['name']}'dan {wind_compare}.
"""
    
    return result

@mcp.tool()
async def havadurumu_aktivite_onerileri(sehir: str) -> str:
    """Belirli bir şehir için hava durumuna göre aktivite önerileri sunar.
    
    Args:
        sehir: Türkiye'deki şehir adı (örn. İstanbul, Ankara)
    """
    # Normalize city name and get coordinates
    normalized_input = normalize_turkish_text(sehir)
    if normalized_input not in TURKISH_CITIES:
        return f"'{sehir}' için bilgi bulunamadı. Lütfen geçerli bir Türk şehri adı girin."
    
    city_data = TURKISH_CITIES[normalized_input]
    lat, lon = city_data["lat"], city_data["lon"]
    
    # Get weather data
    weather_data = await get_current_weather(lat, lon)
    forecast_data = await get_weather_forecast(lat, lon)
    
    if "error" in weather_data:
        if "Demo mode" in weather_data.get("error", ""):
            return generate_demo_activity_recommendations(city_data["name"])
        return f"Hava durumu bilgisi alınamadı: {weather_data['error']}"
    
    # Extract current weather data
    current_temp = weather_data.get("main", {}).get("temp", 20)
    current_condition = weather_data.get("weather", [{}])[0].get("main", "Clear").lower()
    current_id = weather_data.get("weather", [{}])[0].get("id", 800)
    wind_speed = weather_data.get("wind", {}).get("speed", 0)
    rain_1h = weather_data.get("rain", {}).get("1h", 0)
    
    # Check precipitation status (id 2xx: thunderstorm, 3xx: drizzle, 5xx: rain, 6xx: snow)
    is_precipitating = 200 <= current_id < 700
    is_thunderstorm = 200 <= current_id < 300
    is_snowing = 600 <= current_id < 700
    is_clear = 800 <= current_id <= 801
    is_cloudy = 802 <= current_id <= 804
    is_windy = wind_speed > 5.5  # 5.5 m/s is considered moderate wind
    
    # Activity recommendations
    indoor_activities = [
        "Müze ziyareti",
        "Alışveriş merkezi gezisi",
        "Kafe veya restoranda vakit geçirme",
        "Sinema filmi izleme",
        "Kitap okuma",
        "Yerel sergi ziyareti"
    ]
    
    outdoor_activities = [
        "Yürüyüş yapma",
        "Bisiklet sürme",
        "Parkta piknik yapma",
        "Şehir turu",
        "Açık hava kafelerinde oturma",
        "Sahil kenarında gezinme (uygunsa)"
    ]
    
    # Determine activity recommendations based on weather
    if is_precipitating:
        recommended = indoor_activities
        not_recommended = outdoor_activities
        reason = "yağışlı hava" if not is_snowing else "karlı hava"
    elif is_windy:
        recommended = indoor_activities + ["Rüzgardan korunaklı kafelerde oturma"]
        not_recommended = ["Bisiklet sürme", "Parkta piknik yapma", "Açık hava etkinlikleri"]
        reason = "rüzgarlı hava"
    elif current_temp > 30:
        recommended = ["Plaja gitme (uygunsa)", "Su parkı ziyareti", "Gölgeli parklar", "Klimalı mekanlarda vakit geçirme"]
        not_recommended = ["Uzun yürüyüşler", "Güneş altında uzun süre kalmak", "Fiziksel olarak yorucu aktiviteler"]
        reason = "çok sıcak hava"
    elif current_temp < 5:
        recommended = indoor_activities + ["Sıcak içeceklerin tadını çıkarma"]
        not_recommended = ["Uzun süre dışarıda kalmak", "Su aktiviteleri"]
        reason = "soğuk hava"
    else:
        # Nice weather
        recommended = outdoor_activities
        not_recommended = []
        reason = "güzel hava"
    
    result = f"""🎯 {city_data['name']} İÇİN AKTİVİTE ÖNERİLERİ 🎯

📝 GÜNCEL HAVA DURUMU:
• Sıcaklık: {current_temp}°C
• Durum: {weather_data.get("weather", [{}])[0].get("description", "bilinmiyor")}
• Rüzgar: {wind_speed} m/s

👍 ÖNERİLEN AKTİVİTELER ({reason} için):
"""
    
    for activity in recommended[:5]:  # Show at most 5 recommendations
        result += f"• {activity}\n"
        
    if not_recommended:
        result += "\n👎 KAÇINILMASI GEREKEN AKTİVİTELER:\n"
        for activity in not_recommended[:3]:  # Show at most 3 not recommended activities
            result += f"• {activity}\n"
    
    result += f"\n🔮 İLERİYE DÖNÜK TAHMİN:\n"
    
    # Show important changes in future forecast
    if "list" in forecast_data:
        next_day_forecast = None
        for item in forecast_data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            if dt.date() > datetime.now().date():
                next_day_forecast = item
                break
                
        if next_day_forecast:
            next_temp = next_day_forecast["main"]["temp"]
            next_condition = next_day_forecast["weather"][0]["description"]
            next_date = datetime.fromtimestamp(next_day_forecast["dt"]).strftime("%d.%m.%Y")
            
            temp_change = next_temp - current_temp
            temp_change_text = f"{abs(temp_change):.1f}°C daha sıcak" if temp_change > 0 else f"{abs(temp_change):.1f}°C daha soğuk"
            
            result += f"• {next_date} tarihinde hava {temp_change_text} olacak ve {next_condition} bekleniyor."
    
    return result

@mcp.tool()
async def hava_alarmlari() -> str:
    """Türkiye için aktif hava durumu alarmları ve uyarılarını alır."""
    # Note: OpenWeatherMap has alerts but requires a higher tier subscription
    # For a real implementation, you might want to use MGM (Turkish Meteorological Service) data
    return """🚨 TÜRKİYE HAVA DURUMU ALARMLARI 🚨

⚠️ Meteoroloji Genel Müdürlüğü (MGM) tarafından yayınlanan resmi alarm bilgilerini görüntülemek için lütfen MGM'nin resmi web sitesini veya mobil uygulamasını kullanınız.

🔗 https://www.mgm.gov.tr/

Bu fonksiyon şu anda demo amaçlıdır ve gerçek zamanlı alarm verilerine bağlı değildir."""

@mcp.tool()
async def turk_sehirleri_listesi() -> str:
    """Sistemde kayıtlı Türk şehirlerinin listesini döndürür."""
    cities = [f"• {city_data['name']}" for city_name, city_data in sorted(TURKISH_CITIES.items())]
    return "📍 KAYITLI ŞEHİRLER 📍\n\n" + "\n".join(cities)

if __name__ == "__main__":
    # Initialize and run the server
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        print(f"Uygulama başlatılırken bir hata oluştu: {e}")
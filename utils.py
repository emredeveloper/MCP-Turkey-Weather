"""Utility functions for the weather application."""

import unicodedata
from datetime import datetime, timedelta
import random
import math
from typing import Any, Dict, Optional

# Import config for demo functions
from config import TURKISH_CITIES

def normalize_turkish_text(text: str) -> str:
    """Properly normalize Turkish text for case-insensitive comparison."""
    # First convert to lowercase
    text = text.lower()
    # Handle special case of dotted İ -> i and I -> ı
    text = text.replace('İ', 'i').replace('I', 'ı')
    # Replace other Turkish characters
    replacements = {
        'ğ': 'g', 'ü': 'u', 'ş': 's', 'ı': 'i', 
        'ö': 'o', 'ç': 'c', 'â': 'a', 'î': 'i', 'û': 'u'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Remove any remaining diacritics
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    return text

def get_weather_emoji(condition: str) -> str:
    """Returns an emoji based on weather condition."""
    condition = condition.lower()
    
    if "açık" in condition:
        return "☀️"
    elif "az bulutlu" in condition:
        return "🌤️"
    elif "parçalı bulutlu" in condition:
        return "⛅"
    elif "çok bulutlu" in condition:
        return "☁️"
    elif "yağmur" in condition:
        return "🌧️"
    elif "sağanak" in condition:
        return "🌧️"
    elif "kar" in condition:
        return "❄️"
    elif "sis" in condition:
        return "🌫️"
    elif "fırtına" in condition or "gök gürültülü" in condition:
        return "⛈️"
    else:
        return "🌡️"

def get_turkish_day_name(weekday: int) -> str:
    """Returns the Turkish name for the day of the week."""
    days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    return days[weekday]

def get_aqi_recommendations(aqi: int) -> str:
    """Returns recommendations based on the Air Quality Index."""
    if aqi == 1:
        return "Hava kalitesi mükemmel. Açık hava aktivitelerinden güvenle yararlanabilirsiniz."
    elif aqi == 2:
        return "Hava kalitesi iyi. Çoğu insan için açık hava aktiviteleri güvenlidir."
    elif aqi == 3:
        return "Hassas gruplar (astım hastaları, yaşlılar, çocuklar) uzun süreli açık hava aktivitelerini sınırlamalıdır."
    elif aqi == 4:
        return "Herkes açık hava aktivitelerini azaltmalıdır. Hassas gruplar mümkünse içeride kalmalıdır."
    elif aqi == 5:
        return "Sağlık uyarısı: Herkes açık hava aktivitelerini ciddi şekilde sınırlamalı ve mümkünse içeride kalmalıdır."
    else:
        return "Acil durum koşulları: Tüm fiziksel dış mekan aktivitelerinden kaçının ve pencerelerinizi kapalı tutun."

def compare_values(val1, val2, higher_text: str, lower_text: str) -> str:
    """Compares two values and returns descriptive text."""
    try:
        if val1 == "N/A" or val2 == "N/A":
            return "karşılaştırılamıyor"
            
        val1 = float(val1)
        val2 = float(val2)
        
        if val1 > val2:
            return higher_text
        elif val1 < val2:
            return lower_text
        else:
            return "aynı seviyede"
    except:
        return "karşılaştırılamıyor"

# Demo data generation functions
def generate_demo_weather(enlem: float, boylam: float, yer_adi: Optional[str] = None,
                         city_data: Dict[str, Dict[str, Any]] = None) -> str:
    """Generate demo weather data when API key is not available."""
    from datetime import datetime, timedelta
    import random
    
    # Determine location name
    location = "Bilinmeyen Konum"
    if yer_adi:
        location = yer_adi
    elif city_data:
        # Check if coordinates match a known city
        for city in city_data.values():
            if abs(city["lat"] - enlem) < 0.1 and abs(city["lon"] - boylam) < 0.1:
                location = city["name"]
                break
    
    # Generate random but realistic weather data
    conditions = ["açık hava", "az bulutlu", "parçalı bulutlu", "çok bulutlu", 
                  "yağmurlu", "sağanak yağışlı", "gök gürültülü"]
    
    current_temp = round(random.uniform(5, 35), 1)
    current_feels = round(current_temp + random.uniform(-3, 3), 1)
    current_humidity = random.randint(30, 95)
    current_condition = random.choice(conditions)
    wind_speed = round(random.uniform(0, 12), 1)
    wind_dir_text = random.choice(["kuzey", "kuzeydoğu", "doğu", "güneydoğu", "güney", "güneybatı", "batı", "kuzeybatı"])
    
    result = f"""🌤️ HAVA DURUMU: {location.upper()} 🌤️
(DEMO MODU - API anahtarı gerekli)

MEVCUT DURUM:
🌡️ Sıcaklık: {current_temp}°C (Hissedilen: {current_feels}°C)
💧 Nem: %{current_humidity}
🌬️ Rüzgar: {wind_speed} m/s, yönü {wind_dir_text}
🔍 Durum: {current_condition}

5 GÜNLÜK TAHMİN:
"""
    
    # Generate 5-day forecast
    today = datetime.now()
    forecasts = []
    
    for i in range(1, 6):
        date = today + timedelta(days=i)
        temp = round(current_temp + random.uniform(-5, 5), 1)
        condition = random.choice(conditions)
        forecasts.append(f"{date.strftime('%d.%m.%Y')} - {temp}°C, {condition}")
    
    result += "\n".join(forecasts)
    result += "\n\n⚠️ Bu demo verileri yalnızca örnek amaçlıdır. Gerçek hava durumu için geçerli bir API anahtarı ekleyin."
    
    return result

def generate_demo_hourly_forecast(city_name: str, days: int = 1) -> str:
    """Generate demo hourly forecast data."""
    from datetime import datetime, timedelta
    import random
    
    result = f"🕒 {city_name} İÇİN SAATLİK HAVA DURUMU (DEMO) 🕒\n\n"
    
    conditions = ["açık hava", "az bulutlu", "parçalı bulutlu", "çok bulutlu", 
                  "yağmurlu", "sağanak yağışlı", "gök gürültülü"]
    
    current = datetime.now()
    current_date = None
    
    for i in range(days * 24):
        hour = current + timedelta(hours=i)
        
        if current_date != hour.date():
            current_date = hour.date()
            result += f"\n📅 {hour.strftime('%d.%m.%Y')} ({get_turkish_day_name(hour.weekday())})\n"
        
        temp = round(20 + 5 * math.sin(i / 12 * math.pi) + random.uniform(-2, 2), 1)
        condition = random.choice(conditions)
        humidity = random.randint(40, 90)
        wind_speed = round(random.uniform(1, 8), 1)
        
        emoji = get_weather_emoji(condition)
        result += f"{hour.strftime('%H:%M')} - {emoji} {temp}°C, {condition}, Nem: %{humidity}, Rüzgar: {wind_speed}m/s\n"
    
    result += "\n⚠️ Bu demo verileri yalnızca örnek amaçlıdır. Gerçek hava durumu için geçerli bir API anahtarı ekleyin."
    return result

def generate_demo_air_quality(city_name: str) -> str:
    """Generate demo air quality data."""
    import random
    
    aqi = random.randint(1, 5)
    aqi_description = [
        "Bilgi yok",
        "İyi", 
        "Makul", 
        "Hassas gruplar için sağlıksız", 
        "Sağlıksız", 
        "Çok sağlıksız"
    ][min(aqi, 5)]
    
    pm25 = round(random.uniform(5, 50), 1)
    pm10 = round(pm25 * random.uniform(1.2, 2.0), 1)
    o3 = round(random.uniform(20, 180), 1)
    no2 = round(random.uniform(10, 100), 1)
    so2 = round(random.uniform(5, 40), 1)
    co = round(random.uniform(300, 1500), 1)
    
    result = f"""🌬️ {city_name} HAVA KALİTESİ (DEMO) 🌬️

Hava Kalitesi Endeksi (AQI): {aqi} - {aqi_description}

🔍 KİRLETİCİLER:
• Partiküller (PM2.5): {pm25} μg/m³
• Partiküller (PM10): {pm10} μg/m³
• Ozon (O₃): {o3} μg/m³
• Nitrojen dioksit (NO₂): {no2} μg/m³
• Kükürt dioksit (SO₂): {so2} μg/m³
• Karbon monoksit (CO): {co} μg/m³

💡 TAVSİYELER:
{get_aqi_recommendations(aqi)}

⚠️ Bu demo verileri yalnızca örnek amaçlıdır. Gerçek hava kalitesi için geçerli bir API anahtarı ekleyin.
"""
    return result

def generate_demo_city_comparison(city1: str, city2: str) -> str:
    """Generate demo city comparison data."""
    import random
    
    temp1 = round(random.uniform(10, 30), 1)
    temp2 = round(random.uniform(10, 30), 1)
    
    feels1 = round(temp1 + random.uniform(-3, 3), 1)
    feels2 = round(temp2 + random.uniform(-3, 3), 1)
    
    humidity1 = random.randint(30, 90)
    humidity2 = random.randint(30, 90)
    
    conditions = ["açık hava", "az bulutlu", "parçalı bulutlu", "çok bulutlu", "yağmurlu"]
    condition1 = random.choice(conditions)
    condition2 = random.choice(conditions)
    
    wind1 = round(random.uniform(1, 10), 1)
    wind2 = round(random.uniform(1, 10), 1)
    
    # Comparison texts
    temp_compare = compare_values(temp1, temp2, "daha sıcak", "daha soğuk")
    humidity_compare = compare_values(humidity1, humidity2, "daha nemli", "daha kuru")
    wind_compare = compare_values(wind1, wind2, "daha rüzgarlı", "daha sakin")
    
    result = f"""🔄 HAVA DURUMU KARŞILAŞTIRMASI (DEMO) 🔄

┌─────────────────────┬────────────────┬────────────────┐
│                     │ {city1:<14} │ {city2:<14} │
├─────────────────────┼────────────────┼────────────────┤
│ Sıcaklık            │ {temp1}°C          │ {temp2}°C          │
│ Hissedilen          │ {feels1}°C          │ {feels2}°C          │
│ Nem                 │ %{humidity1:<13} │ %{humidity2:<13} │
│ Rüzgar              │ {wind1} m/s         │ {wind2} m/s         │
│ Durum               │ {condition1:<14} │ {condition2:<14} │
└─────────────────────┴────────────────┴────────────────┘

📊 KARŞILAŞTIRMA:
• {city1}, {city2}'dan {temp_compare}.
• {city1}, {city2}'dan {humidity_compare}.
• {city1}, {city2}'dan {wind_compare}.

⚠️ Bu demo verileri yalnızca örnek amaçlıdır. Gerçek karşılaştırma için geçerli bir API anahtarı ekleyin.
"""
    return result

def generate_demo_activity_recommendations(city_name: str) -> str:
    """Generate demo activity recommendations."""
    import random
    
    # Random weather parameters
    current_temp = round(random.uniform(5, 35), 1)
    conditions = ["açık hava", "az bulutlu", "parçalı bulutlu", "çok bulutlu", "yağmurlu", "karlı"]
    current_condition = random.choice(conditions)
    wind_speed = round(random.uniform(0, 10), 1)
    
    # Determine weather scenario
    is_raining = "yağmur" in current_condition
    is_snowing = "kar" in current_condition
    is_clear = "açık" in current_condition or "az bulut" in current_condition
    is_windy = wind_speed > 5.5
    
    # Activity recommendations based on weather
    if is_raining or is_snowing:
        recommended = [
            "Müze ziyareti",
            "Alışveriş merkezi gezisi",
            "Kafe veya restoranda vakit geçirme",
            "Sinema filmi izleme",
            "Kitap okuma"
        ]
        not_recommended = [
            "Yürüyüş yapma",
            "Bisiklet sürme",
            "Parkta piknik yapma",
            "Açık hava etkinlikleri"
        ]
        reason = "yağışlı hava" if is_raining else "karlı hava"
    elif is_windy:
        recommended = [
            "Kapalı mekan aktiviteleri",
            "Rüzgardan korunaklı kafelerde oturma",
            "Müze ziyareti",
            "Alışveriş"
        ]
        not_recommended = ["Bisiklet sürme", "Parkta piknik yapma", "Açık hava etkinlikleri"]
        reason = "rüzgarlı hava"
    elif current_temp > 30:
        recommended = ["Plaja gitme (uygunsa)", "Su parkı ziyareti", "Gölgeli parklar", "Klimalı mekanlarda vakit geçirme"]
        not_recommended = ["Uzun yürüyüşler", "Güneş altında uzun süre kalmak", "Fiziksel olarak yorucu aktiviteler"]
        reason = "çok sıcak hava"
    else:
        recommended = [
            "Yürüyüş yapma",
            "Bisiklet sürme",
            "Parkta piknik yapma",
            "Şehir turu",
            "Açık hava kafelerinde oturma"
        ]
        not_recommended = []
        reason = "güzel hava"
        
    result = f"""🎯 {city_name} İÇİN AKTİVİTE ÖNERİLERİ (DEMO) 🎯

📝 GÜNCEL HAVA DURUMU:
• Sıcaklık: {current_temp}°C
• Durum: {current_condition}
• Rüzgar: {wind_speed} m/s

👍 ÖNERİLEN AKTİVİTELER ({reason} için):
"""
    
    for activity in recommended[:5]:
        result += f"• {activity}\n"
        
    if not_recommended:
        result += "\n👎 KAÇINILMASI GEREKEN AKTİVİTELER:\n"
        for activity in not_recommended[:3]:
            result += f"• {activity}\n"
    
    result += "\n⚠️ Bu demo verileri yalnızca örnek amaçlıdır. Gerçek öneriler için geçerli bir API anahtarı ekleyin."
    return result

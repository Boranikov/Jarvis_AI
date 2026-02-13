import requests
import os
from dotenv import load_dotenv
from config import get_logger

logger = get_logger("skills.weather")

load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(params: dict) -> bool:
    """
    OpenWeatherMap API kullanarak hava durumu bilgisini alır.
    
    Args:
        params: city_name içeren dictionary
        
    Returns:
        Başarılı ise True
    """
    city_name = params.get("city_name", "")
    if not city_name:
        logger.warning("Şehir adı belirtilmedi")
        return False
    
    try:
        response = requests.get(BASE_URL, params={"q": city_name, "appid": API_KEY, "units": "metric", "lang": "tr"})
        data = response.json()
        
        if response.status_code == 200:
            temperature = data["main"]["temp"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            
            logger.info(f"Hava durumu: {city_name}, Sıcaklık: {temperature}°C, Açıklama: {description}, Nem: {humidity}%, Rüzgar Hızı: {wind_speed} m/s")
            return True
        else:
            logger.warning(f"Hava durumu bilgisi alınamadı: {data['message']}")
            return False
    except Exception as e:
        logger.error(f"Hava durumu alma hatası: {e}")
        return False
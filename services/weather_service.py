from typing import Dict

import requests
from loguru import logger

from config import Config


class WeatherService:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = Config.WEATHER_BASE_URL

    def get_weather(self, lat: float, lon: float) -> Dict:
        if not self.api_key:
            return self._mock_weather(lat, lon)

        try:
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric", "lang": "pt_br"}
            resp = requests.get(f"{self.base_url}/weather", params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            return {
                "temperature": data.get("main", {}).get("temp"),
                "description": data.get("weather", [{}])[0].get("description"),
                "humidity": data.get("main", {}).get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "location": data.get("name"),
                "source": "api",
            }
        except Exception as exc:
            logger.warning(f"Erro ao buscar clima: {exc}")
            return self._mock_weather(lat, lon)

    def _mock_weather(self, lat: float, lon: float) -> Dict:
        return {
            "temperature": 25.0,
            "description": "parcialmente nublado (mock)",
            "humidity": 60,
            "wind_speed": 10,
            "location": f"{lat:.2f},{lon:.2f}",
            "source": "mock",
        }

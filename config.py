import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True") == "True"

    OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org")
    OSRM_PROFILE = os.getenv("OSRM_PROFILE", "car")

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

    ANTT_API_URL = "https://dados.antt.gov.br/api"

    CACHE_DIR = os.getenv("CACHE_DIR", "cache")
    CACHE_ROUTES_TTL = 7 * 24 * 60 * 60
    CACHE_TOLL_TTL = 30 * 24 * 60 * 60
    CACHE_WEATHER_TTL = 30 * 60
    CACHE_OSM_TTL = 30 * 24 * 60 * 60

    MAX_ROUTES = int(os.getenv("MAX_ROUTES", 4))
    MAX_WAYPOINTS = int(os.getenv("MAX_WAYPOINTS", 10))

    DEFAULT_COUNTRY = "BR"
    DEFAULT_BBOX = [-73.9872354804, -33.7506355, -28.6341164213, 5.2842873]

    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 60))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")

    USE_OSRM = os.getenv("USE_OSRM", "True") == "True"
    OFFLINE_MODE = os.getenv("OFFLINE_MODE", "False") == "True"

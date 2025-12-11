from fastapi import APIRouter, HTTPException

from api.schemas import (
    OptimizeRequest,
    OptimizeResponse,
    WeatherResponse,
    CacheStatsResponse,
)
from models.point import Point
from models.preferences import Preferences
from services.cache_service import CacheService
from services.routing_service import RoutingService
from services.weather_service import WeatherService

router = APIRouter()

routing_service = RoutingService()
weather_service = WeatherService()
cache_service = CacheService()


@router.post("/optimize-routes", response_model=OptimizeResponse)
def optimize_routes(payload: OptimizeRequest):
    if len(payload.points) < 2:
        raise HTTPException(status_code=400, detail="Informe pelo menos origem e destino")

    points = [Point.from_dict(p.dict()) for p in payload.points]
    preferences = Preferences(**payload.preferences.dict())

    result = routing_service.calculate_optimized_routes(points, preferences)
    return result


@router.get("/weather/{lat}/{lon}", response_model=WeatherResponse)
def get_weather(lat: float, lon: float):
    cache_key = f"{lat:.4f}_{lon:.4f}"
    cached = cache_service.get(cache_key, cache_type="weather")
    if cached:
        cached["cached"] = True
        return cached

    data = weather_service.get_weather(lat, lon)
    if data.get("source") != "mock":
        cache_service.set(cache_key, data, cache_type="weather")
    return data


@router.get("/cache/stats", response_model=CacheStatsResponse)
def cache_stats():
    stats = cache_service.get_stats()
    return stats


@router.delete("/cache/clear")
def clear_cache():
    removed = cache_service.clear_expired()
    return {"removed": removed, "message": "Cache limpo com sucesso"}

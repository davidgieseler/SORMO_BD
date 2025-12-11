import time
from typing import List, Dict

from loguru import logger

from config import Config
from models.point import Point
from models.route import Route
from models.preferences import Preferences
from services.cache_service import CacheService
from services.osrm_service import OSRMService
from services.toll_service import TollService
from services.quality_service import QualityService
from services.optimization_service import OptimizationService
from utils.hash_utils import generate_request_hash


class RoutingService:
    def __init__(self):
        self.osrm = OSRMService()
        self.cache = CacheService()
        self.toll = TollService()
        self.quality = QualityService()
        self.optimizer = OptimizationService()

    def calculate_optimized_routes(self, points: List[Point], preferences: Preferences) -> Dict:
        started = time.perf_counter()
        request_hash = generate_request_hash(points, preferences)

        cached = self.cache.get(request_hash, "routes")
        if cached:
            cached["cached"] = True
            cached.setdefault("calculation_time_ms", 0)
            return cached

        osrm_result = self.osrm.get_route(points, alternatives=True)
        base_routes = osrm_result.get("routes", [])[: Config.MAX_ROUTES]

        processed: List[Route] = []
        for idx, base in enumerate(base_routes):
            geometry = base.get("geometry", [])
            distance_km = base.get("distance_km", 0)
            duration_minutes = base.get("duration_minutes", 0)
            toll_cost = self.toll.calculate_toll_cost(geometry, route_distance_km=distance_km)
            quality_score = self.quality.calculate_quality_score(geometry)
            route_type = self._determine_route_type(idx, preferences)
            color = self._color_for_type(route_type)
            processed.append(
                Route(
                    distance_km=distance_km,
                    duration_minutes=duration_minutes,
                    geometry=geometry,
                    toll_cost_brl=toll_cost,
                    quality_score=quality_score,
                    route_type=route_type,
                    color=color,
                )
            )

        selected_routes = self.optimizer.select_routes(processed, preferences)

        result = {
            "routes": [route.to_dict() for route in selected_routes],
            "cached": False,
            "calculation_time_ms": int((time.perf_counter() - started) * 1000),
        }

        self.cache.set(request_hash, result, "routes")
        return result

    def _determine_route_type(self, index: int, preferences: Preferences) -> str:
        desired = []
        if preferences.fastest:
            desired.append("fastest")
        if preferences.shortest:
            desired.append("shortest")
        if preferences.economical:
            desired.append("economical")
        if preferences.comfortable:
            desired.append("comfortable")
        if index < len(desired):
            return desired[index]
        return "alternative"

    def _color_for_type(self, route_type: str) -> str:
        mapping = {
            "fastest": "#ff4d4f",
            "shortest": "#52c41a",
            "economical": "#1890ff",
            "comfortable": "#faad14",
            "alternative": "#8c8c8c",
        }
        return mapping.get(route_type, "#8c8c8c")

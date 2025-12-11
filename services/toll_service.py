from typing import List, Dict, Optional
from pathlib import Path

import orjson
from loguru import logger

from config import Config
from services.cache_service import CacheService
from utils.geo_utils import haversine_distance_km


class TollService:
    def __init__(self):
        self.cache = CacheService()
        self.toll_data = self._load_toll_data()

    def _load_toll_data(self) -> List[Dict]:
        toll_file = Path(Config.CACHE_DIR) / "toll" / "antt_data.json"
        if toll_file.exists():
            try:
                raw = toll_file.read_bytes()
                data = orjson.loads(raw)
                return data if isinstance(data, list) else []
            except Exception as exc:
                logger.warning(f"Erro lendo dados de pedagio: {exc}")
        return self._get_mock_toll_data()

    def _get_mock_toll_data(self) -> List[Dict]:
        return [
            {"lat": -22.8, "lon": -43.4, "price_car": 12.5},
            {"lat": -23.3, "lon": -46.4, "price_car": 10.2},
        ]

    def calculate_toll_cost(self, geometry: List[tuple], vehicle_type: str = "car", route_distance_km: Optional[float] = None) -> float:
        if not geometry:
            return 0.0

        cost = 0.0
        for toll in self.toll_data:
            if self._route_passes_near_toll(geometry, toll):
                price = toll.get(f"price_{vehicle_type}") or toll.get("price_car") or 0.0
                cost += float(price)

        if cost == 0.0 and route_distance_km:
            cost = max(route_distance_km / 120 * 5, 0)
        return round(cost, 2)

    def _route_passes_near_toll(self, geometry: List[tuple], toll: Dict, threshold_km: float = 1.5) -> bool:
        toll_point = (toll.get("lat"), toll.get("lon"))
        for point in geometry:
            if haversine_distance_km((point[0], point[1]), toll_point) <= threshold_km:
                return True
        return False

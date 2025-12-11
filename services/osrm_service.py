from typing import List, Dict, Optional

import requests
from loguru import logger

from config import Config
from models.point import Point
from utils.geo_utils import path_distance_km


class OSRMService:
    def __init__(self):
        self.base_url = Config.OSRM_BASE_URL.rstrip("/")
        self.profile = Config.OSRM_PROFILE
        self.enabled = Config.USE_OSRM and not Config.OFFLINE_MODE

    def get_route(self, points: List[Point], alternatives: bool = True, steps: bool = False) -> Dict:
        coords = ";".join([f"{p.lon},{p.lat}" for p in points])
        url = f"{self.base_url}/route/v1/{self.profile}/{coords}"
        params = {
            "alternatives": "true" if alternatives else "false",
            "steps": "true" if steps else "false",
            "annotations": "true",
            "geometries": "geojson",
            "overview": "full",
        }

        if not self.enabled:
            logger.info("OSRM desabilitado ou offline, usando rota mock")
            return self._mock_route(points)

        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != "Ok":
                logger.warning(f"OSRM retornou code {data.get('code')} - fallback mock")
                return self._mock_route(points)
            return self._parse_osrm_response(data, points)
        except Exception as exc:
            logger.warning(f"Erro ao conectar com OSRM: {exc} - fallback mock")
            return self._mock_route(points)

    def get_table(self, points: List[Point]) -> Dict:
        coords = ";".join([f"{p.lon},{p.lat}" for p in points])
        url = f"{self.base_url}/table/v1/{self.profile}/{coords}"
        params = {"annotations": "distance,duration"}
        try:
            resp = requests.get(url, params=params, timeout=8)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning(f"Erro no OSRM Table: {exc}")
            raise

    def _parse_osrm_response(self, data: Dict, points: List[Point]) -> Dict:
        routes = []
        for route in data.get("routes", []):
            geometry = route.get("geometry", {}).get("coordinates", [])
            coords = [(latlon[1], latlon[0]) for latlon in geometry]
            distance_km = route.get("distance", 0) / 1000
            duration_min = route.get("duration", 0) / 60
            routes.append({
                "distance_km": distance_km,
                "duration_minutes": duration_min,
                "geometry": coords,
            })
        return {"routes": routes, "waypoints": data.get("waypoints", points)}

    def _mock_route(self, points: List[Point]) -> Dict:
        coords = [(p.lat, p.lon) for p in points]
        distance_km = path_distance_km(coords)
        duration_minutes = distance_km / 80 * 60 if distance_km else 0
        route = {
            "distance_km": distance_km,
            "duration_minutes": duration_minutes,
            "geometry": coords,
        }
        return {"routes": [route], "waypoints": points}

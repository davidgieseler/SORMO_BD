import math
from typing import Tuple, List


def haversine_distance_km(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    r = 6371.0
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def path_distance_km(coords: List[Tuple[float, float]]) -> float:
    if len(coords) < 2:
        return 0.0
    return sum(haversine_distance_km(coords[i], coords[i + 1]) for i in range(len(coords) - 1))

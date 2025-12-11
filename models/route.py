from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import uuid


@dataclass
class Route:
    distance_km: float
    duration_minutes: float
    geometry: List[Tuple[float, float]]
    toll_cost_brl: float = 0.0
    quality_score: float = 5.0
    route_type: str = "alternative"
    color: str = "#0099ff"
    id: str = field(default_factory=lambda: f"route_{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.route_type,
            "color": self.color,
            "distance_km": round(self.distance_km, 3),
            "duration_minutes": round(self.duration_minutes, 2),
            "toll_cost_brl": round(self.toll_cost_brl, 2),
            "quality_score": round(self.quality_score, 2),
            "waypoints": [
                {"lat": lat, "lon": lon} for lat, lon in self.geometry
            ],
        }

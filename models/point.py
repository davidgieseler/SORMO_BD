from dataclasses import dataclass, asdict
from typing import Dict

from utils.validators import validate_lat_lon


@dataclass
class Point:
    lat: float
    lon: float
    type: str = "waypoint"

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Point":
        validate_lat_lon(data.get("lat"), data.get("lon"))
        return cls(lat=float(data["lat"]), lon=float(data["lon"]), type=data.get("type", "waypoint"))

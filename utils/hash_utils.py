import hashlib
import json
from typing import List

from models.point import Point
from models.preferences import Preferences


def generate_request_hash(points: List[Point], preferences: Preferences) -> str:
    data = {
        "points": sorted([(p.lat, p.lon, p.type) for p in points], key=lambda x: (x[0], x[1], x[2])),
        "preferences": preferences.to_dict(),
    }
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.md5(serialized.encode()).hexdigest()

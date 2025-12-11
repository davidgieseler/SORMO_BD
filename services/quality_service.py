from typing import List
import random


class QualityService:
    def calculate_quality_score(self, geometry: List[tuple]) -> float:
        if not geometry:
            return 5.0
        base = 7.0
        noise = random.uniform(-1.0, 1.0)
        score = max(min(base + noise, 10.0), 1.0)
        return round(score, 2)

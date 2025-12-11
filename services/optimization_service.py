from typing import List

from models.route import Route
from models.preferences import Preferences


class OptimizationService:
    def select_routes(self, routes: List[Route], preferences: Preferences) -> List[Route]:
        selected: List[Route] = []
        pool = routes.copy()

        if preferences.fastest and pool:
            fastest = min(pool, key=lambda r: r.duration_minutes)
            selected.append(fastest)
            pool = [r for r in pool if r is not fastest]

        if preferences.shortest and pool:
            shortest = min(pool, key=lambda r: r.distance_km)
            selected.append(shortest)
            pool = [r for r in pool if r is not shortest]

        if preferences.economical and pool:
            economical = min(pool, key=lambda r: r.toll_cost_brl)
            selected.append(economical)
            pool = [r for r in pool if r is not economical]

        if preferences.comfortable and pool:
            comfortable = max(pool, key=lambda r: r.quality_score)
            selected.append(comfortable)
            pool = [r for r in pool if r is not comfortable]

        if not selected:
            selected = routes[:2]
        return selected

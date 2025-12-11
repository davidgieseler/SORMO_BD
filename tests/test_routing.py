from services.routing_service import RoutingService
from models.point import Point
from models.preferences import Preferences


def test_routing_service_returns_route():
    service = RoutingService()
    points = [
        Point(lat=-23.5505, lon=-46.6333, type="origin"),
        Point(lat=-22.9068, lon=-43.1729, type="destination"),
    ]
    prefs = Preferences(fastest=True, shortest=True)
    result = service.calculate_optimized_routes(points, prefs)

    assert "routes" in result
    assert len(result["routes"]) >= 1
    assert result["routes"][0]["distance_km"] >= 0

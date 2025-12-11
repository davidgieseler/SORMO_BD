from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PointSchema(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    type: str = Field("waypoint", description="origin|destination|waypoint")

    @validator("lat")
    def _lat_range(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("lat deve estar entre -90 e 90")
        return v

    @validator("lon")
    def _lon_range(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("lon deve estar entre -180 e 180")
        return v


class PreferencesSchema(BaseModel):
    fastest: bool = True
    shortest: bool = True
    economical: bool = False
    comfortable: bool = False


class OptimizeRequest(BaseModel):
    points: List[PointSchema]
    preferences: PreferencesSchema = PreferencesSchema()
    vehicle_type: str = "car"


class RouteOut(BaseModel):
    id: str
    type: str
    color: str
    distance_km: float
    duration_minutes: float
    toll_cost_brl: float
    quality_score: float
    waypoints: List[dict]


class OptimizeResponse(BaseModel):
    routes: List[RouteOut]
    cached: bool
    calculation_time_ms: int


class WeatherResponse(BaseModel):
    temperature: float
    description: str
    humidity: float
    wind_speed: float
    location: str


class CacheStatsResponse(BaseModel):
    routes: dict
    osm: dict
    toll: dict
    weather: dict
    removed: Optional[int] = None

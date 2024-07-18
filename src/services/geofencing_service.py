from shapely.geometry import Point, Polygon
from typing import List, Dict

class GeofencingService:
    def __init__(self, service_areas: List[List[Dict[str, float]]]):
        self.service_areas = [Polygon(area) for area in service_areas]

    def is_location_allowed(self, location: Dict[str, float]) -> bool:
        point = Point(location['lon'], location['lat'])
        return any(area.contains(point) for area in self.service_areas)

# src/utils/config.py

SERVICE_AREAS = [
    [
        {"lat": 31.9399, "lon": 117.6816}, # 肥东
        {"lat": 31.7551, "lon": 117.3828}, # 包河
        {"lat": 31.6524, "lon": 116.9354}, # 肥西
    ],
]
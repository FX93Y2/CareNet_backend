from shapely.geometry import Point, Polygon
from typing import List, Dict

class GeofencingService:
    def __init__(self, service_areas: List[List[Dict[str, float]]]):
        self.service_areas = [Polygon(area) for area in service_areas]

    def is_location_allowed(self, location: Dict[str, float]) -> bool:
        point = Point(location['lon'], location['lat'])
        return any(area.contains(point) for area in self.service_areas)

# src/utils/config.py


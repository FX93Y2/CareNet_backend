from math import radians, sin, cos, sqrt, atan2
from src.models.schemas import Location

class DistanceService:
    @staticmethod
    def calculate_distance(loc1: Location, loc2: Location) -> float:
        # Haversine formula
        R = 6371  # Earth's radius in kilometers

        lat1, lon1 = radians(loc1.latitude), radians(loc1.longitude)
        lat2, lon2 = radians(loc2.latitude), radians(loc2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        distance = R * c
        return distance
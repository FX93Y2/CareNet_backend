import pytest
from services.geofencing_service import GeofencingService
from utils.config import SERVICE_AREAS

@pytest.fixture
def geofencing_service():
    return GeofencingService(SERVICE_AREAS)

def test_is_location_allowed_inside():
    service = GeofencingService(SERVICE_AREAS)
    assert service.is_location_allowed({"lat": 40.7500, "lon": -73.9500}) == True

def test_is_location_allowed_outside():
    service = GeofencingService(SERVICE_AREAS)
    assert service.is_location_allowed({"lat": 41.0000, "lon": -75.0000}) == False
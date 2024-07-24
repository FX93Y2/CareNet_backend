import pytest
import os
import logging
import json
from dotenv import load_dotenv
from src.services.geofencing_service import GeofencingService
from src.models.schemas import Location
from src.utils.config import Settings
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def settings():
    return Settings(
        ARCGIS_PORTAL_URL=os.getenv("ARCGIS_PORTAL_URL"),
        ARCGIS_API_KEY=os.getenv("ARCGIS_API_KEY"),
        SERVICE_AREA_LAYER_URL=os.getenv("SERVICE_AREA_LAYER_URL")
    )

@pytest.fixture(scope="module")
def geofencing_service(settings):
    try:
        logger.info(f"Initializing GeofencingService with settings: {settings}")
        service = GeofencingService(settings)
        logger.info("GeofencingService initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize GeofencingService: {str(e)}", exc_info=True)
        raise

@pytest.mark.integration
def test_direct_layer_query(settings):
    gis = GIS(settings.ARCGIS_PORTAL_URL, api_key=settings.ARCGIS_API_KEY)
    service_area_layer = FeatureLayer(settings.SERVICE_AREA_LAYER_URL, gis)
    
    query_result = service_area_layer.query(
        where="1=1",
        out_fields="*",
        return_geometry=True,
        geometry_precision=6,
        out_sr=4326
    )
    
    logger.info(f"Direct layer query result: {json.dumps(query_result.to_dict(), indent=2)}")
    
    assert query_result.features, "Query should return features"

@pytest.mark.integration
def test_service_area_initialization(geofencing_service):
    logger.info(f"Service area: {geofencing_service.service_area}")
    if geofencing_service.service_area is None:
        logger.warning("Service area is None, check if the layer is empty")
    else:
        logger.info(f"Service area geometry type: {geofencing_service.service_area.type}")
        logger.info(f"Service area JSON: {json.dumps(geofencing_service.service_area.as_dict(), indent=2)}")
    assert geofencing_service.service_area is not None, "Service area should be initialized"

@pytest.mark.integration
def test_location_inside_service_area(geofencing_service):
    location = Location(latitude=31.889, longitude=117.361)
    result = geofencing_service.is_location_allowed(location)
    logger.info(f"Is location {location} allowed: {result}")
    assert result, "Location should be inside service area"

@pytest.mark.integration
def test_location_outside_service_area(geofencing_service):
    location = Location(latitude=32.0, longitude=118.0)
    result = geofencing_service.is_location_allowed(location)
    logger.info(f"Is location {location} allowed: {result}")
    assert not result, "Location should be outside service area"

@pytest.mark.integration
def test_invalid_service_area_url(settings):
    settings.SERVICE_AREA_LAYER_URL = "https://invalid-url.com"
    
    start_time = time.time()
    timeout = 10  # 10 seconds timeout
    
    with pytest.raises(Exception):
        service = GeofencingService(settings)
        while time.time() - start_time < timeout:
            if service.service_area is not None:
                break
            time.sleep(0.1)
        else:
            pytest.fail("Timeout while waiting for invalid service area response")

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
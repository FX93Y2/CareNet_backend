import pytest
from unittest.mock import Mock, patch
from src.services.geofencing_service import GeofencingService
from src.models.schemas import Location
from src.utils.config import Settings
from arcgis.geometry import Geometry, Point

class MockGeometry:
    def __init__(self, contains_result=True):
        self.contains_result = contains_result

    def contains(self, point):
        return self.contains_result

@pytest.fixture
def mock_settings():
    return Mock(spec=Settings, ARCGIS_PORTAL_URL="http://mock-portal.com", 
                ARCGIS_API_KEY="mock-api-key", 
                SERVICE_AREA_LAYER_URL="http://mock-service-area-layer.com")

@pytest.fixture
def mock_gis():
    return Mock()

@pytest.fixture
def mock_feature_layer():
    mock_feature = Mock()
    mock_feature.geometry = {'type': 'Polygon', 'coordinates': [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}
    mock_query = Mock()
    mock_query.features = [mock_feature]
    mock_layer = Mock()
    mock_layer.query.return_value = mock_query
    return mock_layer

@pytest.fixture
def geofencing_service(mock_settings, mock_gis, mock_feature_layer):
    with patch('src.services.geofencing_service.FeatureLayer', return_value=mock_feature_layer):
        with patch('src.services.geofencing_service.Geometry', return_value=MockGeometry()):
            service = GeofencingService(settings=mock_settings, gis=mock_gis)
            return service

def test_is_location_allowed_inside(geofencing_service):
    location = Location(latitude=31.88, longitude=117.35)
    geofencing_service.service_area = MockGeometry(contains_result=True)
    
    result = geofencing_service.is_location_allowed(location)
    
    assert result is True

def test_is_location_allowed_outside(geofencing_service):
    location = Location(latitude=32.0, longitude=118.0)
    geofencing_service.service_area = MockGeometry(contains_result=False)
    
    result = geofencing_service.is_location_allowed(location)
    
    assert result is False

def test_is_location_allowed_error(geofencing_service):
    location = Location(latitude=31.88, longitude=117.35)
    geofencing_service.service_area = MockGeometry()
    geofencing_service.service_area.contains = Mock(side_effect=Exception("Test error"))
    
    result = geofencing_service.is_location_allowed(location)
    
    assert result is False
    geofencing_service.service_area.contains.assert_called_once()

@patch('src.services.geofencing_service.FeatureLayer')
def test_get_service_area_success(mock_feature_layer, mock_gis, mock_settings):
    mock_feature = Mock()
    mock_feature.geometry = {'type': 'Polygon', 'coordinates': [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}
    mock_feature_layer.return_value.query.return_value.features = [mock_feature]
    
    service = GeofencingService(settings=mock_settings, gis=mock_gis)
    
    assert isinstance(service.service_area, Geometry)

@patch('src.services.geofencing_service.FeatureLayer')
def test_get_service_area_no_features(mock_feature_layer, mock_gis, mock_settings):
    mock_feature_layer.return_value.query.return_value.features = []
    
    with pytest.raises(ValueError, match="No features found in the service area layer"):
        GeofencingService(settings=mock_settings, gis=mock_gis)

@patch('src.services.geofencing_service.FeatureLayer')
def test_get_service_area_invalid_geometry(mock_feature_layer, mock_gis, mock_settings):
    mock_feature = Mock()
    mock_feature.geometry = None
    mock_feature_layer.return_value.query.return_value.features = [mock_feature]
    
    with pytest.raises(ValueError, match="Invalid geometry in the service area feature"):
        GeofencingService(settings=mock_settings, gis=mock_gis)
import pytest
import logging
from unittest.mock import AsyncMock, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi import status
from src.models.schemas import CareRequest, CareRequestUpdate, CareRequestStatus, Location, ServiceType, UrgencyLevel
from src.services.care_request_service import CareRequestService
from src.services.geofencing_service import GeofencingService
from src.services.task_scheduler_service import TaskSchedulerService
from src.utils.error_handling import AppException

@pytest.fixture
def mock_db_client():
    mock_client = AsyncMock(spec=AsyncIOMotorClient)
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_client.test_database = mock_db
    mock_db.care_requests = mock_collection
    return mock_client

@pytest.fixture(scope="function")
def mock_geofencing_service():
    return MagicMock(spec=GeofencingService)

@pytest.fixture(scope="function")
def mock_task_scheduler_service():
    return AsyncMock(spec=TaskSchedulerService)

@pytest.fixture
def care_request_service(mock_db_client):
    geofencing_service = MagicMock(spec=GeofencingService)
    task_scheduler_service = AsyncMock(spec=TaskSchedulerService)
    return CareRequestService(mock_db_client, geofencing_service, task_scheduler_service)

@pytest.fixture(scope="function")
def sample_care_request():
    return CareRequest(
        client_id=str(ObjectId()),
        service_type=ServiceType.MEDICAL_CHECKUP,
        urgency=UrgencyLevel.NORMAL,
        location=Location(latitude=40.7128, longitude=-74.0060),
        status=CareRequestStatus.PENDING
    )

@pytest.fixture(scope="function")
def mock_collection():
    return AsyncMock()

@pytest.mark.asyncio
async def test_create_care_request_success(care_request_service, sample_care_request, mock_collection, monkeypatch):
    care_request_service.geofencing.is_location_allowed.return_value = True
    mock_collection.insert_one.return_value = AsyncMock(inserted_id=ObjectId("60d5ec9f1c9d440000000000"))
    monkeypatch.setattr("src.services.care_request_service.get_care_requests_collection", AsyncMock(return_value=mock_collection))

    result = await care_request_service.create_care_request(sample_care_request)

    assert result == "60d5ec9f1c9d440000000000"
    care_request_service.geofencing.is_location_allowed.assert_called_once_with(sample_care_request.location)
    expected_dict = sample_care_request.model_dump(exclude={"id"})
    mock_collection.insert_one.assert_called_once_with(expected_dict)
    care_request_service.scheduler.schedule_new_request.assert_called_once_with("60d5ec9f1c9d440000000000")

@pytest.mark.asyncio
async def test_get_care_request_not_found(care_request_service, mock_collection, monkeypatch):
    mock_id = "60d5ec9f1c9d440000000000"
    mock_collection.find_one.return_value = None
    monkeypatch.setattr("src.services.care_request_service.get_care_requests_collection", AsyncMock(return_value=mock_collection))

    with pytest.raises(AppException) as exc_info:
        await care_request_service.get_care_request(mock_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Care request not found"

@pytest.mark.asyncio
async def test_update_care_request_not_found(care_request_service, mock_collection, monkeypatch):
    mock_id = "60d5ec9f1c9d440000000000"
    update_data = CareRequestUpdate(status=CareRequestStatus.IN_PROGRESS)
    mock_collection.update_one.return_value = AsyncMock(modified_count=0)
    monkeypatch.setattr("src.services.care_request_service.get_care_requests_collection", AsyncMock(return_value=mock_collection))

    with pytest.raises(AppException) as exc_info:
        await care_request_service.update_care_request(mock_id, update_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Care request not found or no changes made"

@pytest.mark.asyncio
async def test_delete_care_request_success(care_request_service, mock_collection, monkeypatch):
    mock_id = "60d5ec9f1c9d440000000000"
    mock_collection.delete_one.return_value = AsyncMock(deleted_count=1)
    monkeypatch.setattr("src.services.care_request_service.get_care_requests_collection", AsyncMock(return_value=mock_collection))

    await care_request_service.delete_care_request(mock_id)

    mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(mock_id)})

@pytest.mark.asyncio
async def test_delete_care_request_not_found(care_request_service, mock_collection, monkeypatch):
    mock_id = "60d5ec9f1c9d440000000000"
    mock_collection.delete_one.return_value = AsyncMock(deleted_count=0)
    monkeypatch.setattr("src.services.care_request_service.get_care_requests_collection", AsyncMock(return_value=mock_collection))

    with pytest.raises(AppException) as exc_info:
        await care_request_service.delete_care_request(mock_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Care request not found"

@pytest.mark.asyncio
async def test_list_care_requests(care_request_service, sample_care_request, caplog, monkeypatch):
    caplog.set_level(logging.DEBUG)

    # Create a mock for the collection
    mock_collection = AsyncMock()

    # Create a mock for the cursor
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[sample_care_request.model_dump(exclude={"id"})])

    # Set up the mock collection to return the mock cursor
    mock_collection.find = MagicMock(return_value=mock_cursor)

    async def mock_get_care_requests_collection():
        return mock_collection

    monkeypatch.setattr("src.services.care_request_service.get_care_requests_collection", mock_get_care_requests_collection)

    result = await care_request_service.list_care_requests(skip=0, limit=10)

    assert len(result) == 1
    assert isinstance(result[0], CareRequest)
    assert result[0].client_id == sample_care_request.client_id

    mock_collection.find.assert_called_once()
    mock_cursor.skip.assert_called_once_with(0)
    mock_cursor.limit.assert_called_once_with(10)
    mock_cursor.to_list.assert_called_once_with(length=10)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   

@pytest.fixture
def mock_motor_client(monkeypatch):
    mock_client = AsyncMock()
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    monkeypatch.setattr("motor.motor_asyncio.AsyncIOMotorClient", MagicMock(return_value=mock_client))
    return mock_collection


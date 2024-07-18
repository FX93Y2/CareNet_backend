from datetime import datetime
from typing import List, Optional
import sys
import asyncio
from pathlib import Path
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock, MagicMock
from src.models.schemas import CareRequest, CareRequestStatus, ServiceType, UrgencyLevel
from src.services.care_request_service import CareRequestService
from src.database.mongodb import Database, db
from src.services.geofencing_service import GeofencingService
from src.services.task_scheduler_service import TaskSchedulerService

root_dir = Path(__file__).parent.parent.absolute()

# Add the project root to the Python path
sys.path.insert(0, str(root_dir))

@pytest.fixture
def care_request_service():
    db_client = AsyncMock(spec=AsyncIOMotorClient)
    geofencing_service = MagicMock(spec=GeofencingService)
    task_scheduler_service = AsyncMock(spec=TaskSchedulerService)
    return CareRequestService(db_client, geofencing_service, task_scheduler_service)

@pytest.fixture
def sample_care_request():
    return CareRequest(
        client_id='6698bbacadba77358958e38c',
        service_type=ServiceType.MEDICAL_CHECKUP,
        urgency=UrgencyLevel.HIGH,
        status=CareRequestStatus.PENDING,
        created_at=datetime.now(),
        location={"latitude": 40.7128, "longitude": -74.0060}
    )

@pytest.fixture(autouse=True)
def mock_db_connection(monkeypatch):
    async def mock_get_database():
        return AsyncMock()
    
    monkeypatch.setattr(Database, "client", AsyncMock(spec=AsyncIOMotorClient))
    monkeypatch.setattr("src.database.mongodb.get_database", mock_get_database)

@pytest.fixture
def mock_motor_client(monkeypatch):
    mock_client = AsyncMock(spec=AsyncIOMotorClient)
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    monkeypatch.setattr("motor.motor_asyncio.AsyncIOMotorClient", MagicMock(return_value=mock_client))
    return mock_collection

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
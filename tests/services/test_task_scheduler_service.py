import pytest
from unittest.mock import AsyncMock
from services.task_scheduler_service import TaskSchedulerService
from models.schemas import CareRequestStatus

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def task_scheduler_service(mock_db):
    return TaskSchedulerService(mock_db)

@pytest.mark.asyncio
async def test_schedule_new_request(task_scheduler_service):
    request_id = "60d5ec9f1c9d440000000000"
    await task_scheduler_service.schedule_new_request(request_id)
    task_scheduler_service.db.care_requests.update_one.assert_called_once_with(
        {"_id": request_id},
        {"$set": {"status": CareRequestStatus.PENDING}}
    )
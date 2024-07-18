from fastapi import Depends
from database.mongodb import get_database
from services.care_request_service import CareRequestService
from services.geofencing_service import GeofencingService
from services.task_scheduler_service import TaskSchedulerService
from utils.config import SERVICE_AREAS

async def get_care_request_service(db=Depends(get_database)):
    geofencing_service = GeofencingService(SERVICE_AREAS)
    task_scheduler_service = TaskSchedulerService(db)
    return CareRequestService(db, geofencing_service, task_scheduler_service)
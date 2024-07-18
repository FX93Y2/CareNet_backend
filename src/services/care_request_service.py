from bson import ObjectId
from fastapi import status
from src.models.schemas import CareRequest, CareRequestUpdate, CareRequestStatus
from src.database.mongodb import get_care_requests_collection
from src.services.geofencing_service import GeofencingService
from src.services.task_scheduler_service import TaskSchedulerService
from src.utils.error_handling import AppException

class CareRequestService:
    def __init__(self, geofencing: GeofencingService, scheduler: TaskSchedulerService):
        self.geofencing = geofencing
        self.scheduler = scheduler

    async def create_care_request(self, care_request: CareRequest) -> str:
        if not self.geofencing.is_location_allowed(care_request.location):
            raise AppException(status_code=status.HTTP_400_BAD_REQUEST, 
                               detail="Location is outside of service area")
        
        collection = await get_care_requests_collection()
        care_request_dict = care_request.model_dump(exclude={"id"})
        result = await collection.insert_one(care_request_dict)
        await self.scheduler.schedule_new_request(str(result.inserted_id))
        return str(result.inserted_id)

    async def get_care_request(self, request_id: str) -> CareRequest:
        collection = await get_care_requests_collection()
        care_request = await collection.find_one({"_id": ObjectId(request_id)})
        if care_request is None:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care request not found")
        return CareRequest(**care_request)

    async def update_care_request(self, request_id: str, updates: CareRequestUpdate) -> CareRequest:
        collection = await get_care_requests_collection()
        update_data = updates.model_dump(exclude_unset=True)
        result = await collection.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care request not found or no changes made")
        return await self.get_care_request(request_id)

    async def delete_care_request(self, request_id: str) -> None:
        collection = await get_care_requests_collection()
        result = await collection.delete_one({"_id": ObjectId(request_id)})
        if result.deleted_count == 0:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care request not found")

    async def list_care_requests(self, skip: int = 0, limit: int = 100) -> list[CareRequest]:
        collection = await get_care_requests_collection()
        cursor = await collection.find()
        cursor = await cursor.skip(skip).limit(limit).to_list(length=limit)
        return [CareRequest(**doc) for doc in cursor]


    async def get_requests_by_status(self, status: CareRequestStatus) -> list[CareRequest]:
        collection = await get_care_requests_collection()
        cursor = await collection.find({"status": status})
        cursor = await cursor.to_list(length=None)
        return [CareRequest(**doc) for doc in cursor]
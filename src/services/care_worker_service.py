from typing import List, Optional
from bson import ObjectId
from fastapi import status
from src.models.schemas import CareWorker, CareWorkerCreate, CareWorkerUpdate, CareWorkerStatus
from src.database.mongodb import get_care_workers_collection
from src.utils.error_handling import AppException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CareWorkerService:
    @staticmethod
    async def create_care_worker(care_worker: CareWorkerCreate) -> str:
        collection = await get_care_workers_collection()
        care_worker_dict = care_worker.model_dump(exclude={"password"})
        care_worker_dict["password"] = pwd_context.hash(care_worker.password)
        result = await collection.insert_one(care_worker_dict)
        return str(result.inserted_id)

    @staticmethod
    async def get_care_worker(worker_id: str) -> CareWorker:
        collection = await get_care_workers_collection()
        care_worker = await collection.find_one({"_id": ObjectId(worker_id)})
        if care_worker is None:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care worker not found")
        return CareWorker(**care_worker)

    @staticmethod
    async def update_care_worker(worker_id: str, updates: CareWorkerUpdate) -> CareWorker:
        collection = await get_care_workers_collection()
        update_data = updates.model_dump(exclude_unset=True)
        result = await collection.update_one(
            {"_id": ObjectId(worker_id)},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care worker not found or no changes made")
        return await CareWorkerService.get_care_worker(worker_id)

    @staticmethod
    async def delete_care_worker(worker_id: str) -> bool:
        collection = await get_care_workers_collection()
        result = await collection.delete_one({"_id": ObjectId(worker_id)})
        return result.deleted_count > 0

    @staticmethod
    async def list_care_workers(skip: int = 0, limit: int = 100) -> List[CareWorker]:
        collection = await get_care_workers_collection()
        cursor = collection.find().skip(skip).limit(limit)
        care_workers = await cursor.to_list(length=limit)
        return [CareWorker(**cw) for cw in care_workers]

    @staticmethod
    async def get_available_care_workers_in_area(latitude: float, longitude: float, max_distance: float) -> List[CareWorker]:
        collection = await get_care_workers_collection()
        query = {
            "current_location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": max_distance
                }
            },
            "status": CareWorkerStatus.AVAILABLE
        }
        cursor = collection.find(query)
        care_workers = await cursor.to_list(length=None)
        return [CareWorker(**cw) for cw in care_workers]
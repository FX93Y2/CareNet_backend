from typing import List
import json
from bson import ObjectId
from fastapi import status
from src.models.schemas import CareWorker, CareWorkerCreate, CareWorkerUpdate, CareWorkerStatus
from src.database.mongodb import get_care_workers_collection
from src.services.redis_cache_service import RedisCacheService
from src.utils.error_handling import AppException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CareWorkerService:
    def __init__(self):
        self.redis_cache = RedisCacheService()

    async def initialize(self):
        await self.redis_cache.initialize()

    async def create_care_worker(self, care_worker: CareWorkerCreate) -> str:
        collection = await get_care_workers_collection()
        care_worker_dict = care_worker.model_dump(exclude={"password"})
        care_worker_dict["password"] = pwd_context.hash(care_worker.password)
        result = await collection.insert_one(care_worker_dict)
        worker_id = str(result.inserted_id)
        
        # Add worker to Redis geospatial index
        await self.redis_cache.geoadd("care_workers_locations", 
                                      care_worker.current_location.longitude,
                                      care_worker.current_location.latitude,
                                      worker_id)
        
        return worker_id

    async def get_care_worker(self, worker_id: str) -> CareWorker:
        # Try to get from cache first
        cached_worker = await self.redis_cache.get(f"care_worker:{worker_id}")
        if cached_worker:
            return CareWorker(**json.loads(cached_worker))
        
        # If not in cache, get from database
        collection = await get_care_workers_collection()
        care_worker = await collection.find_one({"_id": ObjectId(worker_id)})
        if care_worker is None:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care worker not found")
        
        # Cache the worker data
        await self.redis_cache.set(f"care_worker:{worker_id}", json.dumps(care_worker), expire=3600)
        
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

    async def get_available_care_workers_in_area(self, latitude: float, longitude: float, max_distance: float) -> List[CareWorker]:
        worker_ids = await self.redis_cache.georadius("care_workers_locations", longitude, latitude, max_distance)
        
        workers = []
        for worker_id in worker_ids:
            worker = await self.get_care_worker(worker_id)
            if worker.status == CareWorkerStatus.AVAILABLE:
                workers.append(worker)
        
        return workers
    
    async def close(self):
        await self.redis_cache.close()
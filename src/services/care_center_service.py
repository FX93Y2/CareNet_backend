from typing import List
from bson import ObjectId
from fastapi import status
from src.models.schemas import CareCenter, CareCenterCreate, CareCenterUpdate
from src.database.mongodb import get_collection
from src.utils.error_handling import AppException

class CareCenterService:
    async def create_care_center(self, care_center: CareCenterCreate) -> str:
        collection = await get_collection("care_centers")
        care_center_dict = care_center.model_dump()
        result = await collection.insert_one(care_center_dict)
        return str(result.inserted_id)

    async def get_care_center(self, center_id: str) -> CareCenter:
        collection = await get_collection("care_centers")
        care_center = await collection.find_one({"_id": ObjectId(center_id)})
        if care_center is None:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care center not found")
        return CareCenter(**care_center)

    async def update_care_center(self, center_id: str, updates: CareCenterUpdate) -> CareCenter:
        collection = await get_collection("care_centers")
        update_data = updates.model_dump(exclude_unset=True)
        result = await collection.update_one(
            {"_id": ObjectId(center_id)},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise AppException(status_code=status.HTTP_404_NOT_FOUND, 
                               detail="Care center not found or no changes made")
        return await self.get_care_center(center_id)

    async def list_care_centers(self, skip: int = 0, limit: int = 100) -> List[CareCenter]:
        collection = await get_collection("care_centers")
        cursor = collection.find().skip(skip).limit(limit)
        care_centers = await cursor.to_list(length=limit)
        return [CareCenter(**cc) for cc in care_centers]

    async def get_care_centers_in_area(self, latitude: float, longitude: float, max_distance: float) -> List[CareCenter]:
        collection = await get_collection("care_centers")
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": max_distance
                }
            }
        }
        cursor = collection.find(query)
        care_centers = await cursor.to_list(length=None)
        return [CareCenter(**cc) for cc in care_centers]
from fastapi import APIRouter, Depends, Query
from typing import List
from src.models.schemas import CareCenter, CareCenterCreate, CareCenterUpdate
from src.services.care_center_service import CareCenterService

router = APIRouter()

@router.post("/care-centers", response_model=str)
async def create_care_center(care_center: CareCenterCreate, service: CareCenterService = Depends()):
    return await service.create_care_center(care_center)

@router.get("/care-centers/{center_id}", response_model=CareCenter)
async def get_care_center(center_id: str, service: CareCenterService = Depends()):
    return await service.get_care_center(center_id)

@router.put("/care-centers/{center_id}", response_model=CareCenter)
async def update_care_center(center_id: str, updates: CareCenterUpdate, service: CareCenterService = Depends()):
    return await service.update_care_center(center_id, updates)

@router.get("/care-centers", response_model=List[CareCenter])
async def list_care_centers(skip: int = 0, limit: int = 100, service: CareCenterService = Depends()):
    return await service.list_care_centers(skip, limit)

@router.get("/care-centers/nearby", response_model=List[CareCenter])
async def get_nearby_care_centers(
    latitude: float = Query(..., description="Latitude of the center point"),
    longitude: float = Query(..., description="Longitude of the center point"),
    max_distance: float = Query(10000, description="Maximum distance in meters"),
    service: CareCenterService = Depends()
):
    return await service.get_care_centers_in_area(latitude, longitude, max_distance)
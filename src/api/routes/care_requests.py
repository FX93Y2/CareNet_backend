from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.models.schemas import CareRequest, CareRequestCreate, CareRequestUpdate, CareRequestStatus
from src.services.care_request_service import CareRequestService
from src.services.geofencing_service import GeofencingService
from src.utils.config import Settings

router = APIRouter()

def get_geofencing_service():
    settings = Settings()
    return GeofencingService(settings)

def get_care_request_service():
    return CareRequestService()

@router.post("/care-requests", response_model=str)
async def create_care_request(
    care_request: CareRequestCreate,
    service: CareRequestService = Depends(get_care_request_service),
    geofencing: GeofencingService = Depends(get_geofencing_service)
):
    if not geofencing.is_location_allowed(care_request.location):
        raise HTTPException(status_code=400, detail="Location is not within the service area")
    return await service.create_care_request(care_request)

@router.get("/care-requests/{request_id}", response_model=CareRequest)
async def get_care_request(
    request_id: str, 
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.get_care_request(request_id)

@router.put("/care-requests/{request_id}", response_model=CareRequest)
async def update_care_request(
    request_id: str, 
    updates: CareRequestUpdate, 
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.update_care_request(request_id, updates)

@router.put("/care-requests/{request_id}/assign/{worker_id}", response_model=CareRequest)
async def assign_care_worker(
    request_id: str, 
    worker_id: str, 
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.assign_care_worker(request_id, worker_id)

@router.get("/care-requests", response_model=List[CareRequest])
async def list_care_requests(
    skip: int = 0, 
    limit: int = 100, 
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.list_care_requests(skip, limit)

@router.get("/care-requests/by-status/{status}", response_model=List[CareRequest])
async def get_requests_by_status(
    status: CareRequestStatus, 
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.get_requests_by_status(status)
from fastapi import APIRouter, Depends, Query
from typing import List
from src.models.schemas import CareRequest, CareRequestCreate, CareRequestUpdate, CareRequestStatus
from src.services.care_request_service import CareRequestService

router = APIRouter()

@router.post("/care-requests", response_model=str)
async def create_care_request(care_request: CareRequestCreate, service: CareRequestService = Depends()):
    return await service.create_care_request(care_request)

@router.get("/care-requests/{request_id}", response_model=CareRequest)
async def get_care_request(request_id: str, service: CareRequestService = Depends()):
    return await service.get_care_request(request_id)

@router.put("/care-requests/{request_id}", response_model=CareRequest)
async def update_care_request(request_id: str, updates: CareRequestUpdate, service: CareRequestService = Depends()):
    return await service.update_care_request(request_id, updates)

@router.put("/care-requests/{request_id}/assign/{worker_id}", response_model=CareRequest)
async def assign_care_worker(request_id: str, worker_id: str, service: CareRequestService = Depends()):
    return await service.assign_care_worker(request_id, worker_id)

@router.get("/care-requests", response_model=List[CareRequest])
async def list_care_requests(skip: int = 0, limit: int = 100, service: CareRequestService = Depends()):
    return await service.list_care_requests(skip, limit)

@router.get("/care-requests/by-status/{status}", response_model=List[CareRequest])
async def get_requests_by_status(status: CareRequestStatus, service: CareRequestService = Depends()):
    return await service.get_requests_by_status(status)
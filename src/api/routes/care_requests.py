# src/api/routes/care_requests.py

from fastapi import APIRouter, Depends, Query, Security
from typing import List
from models.schemas import CareRequest, CareRequestCreate, CareRequestUpdate, CareRequestStatus
from services.care_request_service import CareRequestService
from api.dependencies import get_care_request_service
from api.auth import get_current_active_user, TokenData

router = APIRouter()

@router.post("/care-requests", response_model=str)
async def create_care_request(
    care_request: CareRequestCreate,
    current_user: TokenData = Security(get_current_active_user, scopes=["create:care_request"]),
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.create_care_request(care_request)

@router.get("/care-requests/{request_id}", response_model=CareRequest)
async def get_care_request(
    request_id: str,
    current_user: TokenData = Security(get_current_active_user, scopes=["read:care_request"]),
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.get_care_request(request_id)

@router.put("/care-requests/{request_id}", response_model=CareRequest)
async def update_care_request(
    request_id: str,
    updates: CareRequestUpdate,
    current_user: TokenData = Security(get_current_active_user, scopes=["update:care_request"]),
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.update_care_request(request_id, updates)

@router.delete("/care-requests/{request_id}", response_model=None)
async def delete_care_request(
    request_id: str,
    current_user: TokenData = Security(get_current_active_user, scopes=["delete:care_request"]),
    service: CareRequestService = Depends(get_care_request_service)
):
    await service.delete_care_request(request_id)
    return {"detail": "Care request deleted successfully"}

@router.post("/care-requests/{request_id}/assign/{worker_id}", response_model=CareRequest)
async def assign_worker_to_request(
    request_id: str,
    worker_id: str,
    current_user: TokenData = Security(get_current_active_user, scopes=["assign:care_request"]),
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.assign_worker(request_id, worker_id)

@router.get("/care-requests", response_model=List[CareRequest])
async def list_care_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Security(get_current_active_user, scopes=["read:care_request"]),
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.list_care_requests(skip, limit)

@router.get("/care-requests/status/{status}", response_model=List[CareRequest])
async def get_requests_by_status(
    status: CareRequestStatus,
    current_user: TokenData = Security(get_current_active_user, scopes=["read:care_request"]),
    service: CareRequestService = Depends(get_care_request_service)
):
    return await service.get_requests_by_status(status) 
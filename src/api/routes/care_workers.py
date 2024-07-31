from fastapi import APIRouter, HTTPException, Depends, status
from src.services.care_worker_service import CareWorkerService
from src.models.schemas import CareWorker, CareWorkerStatus, CareWorkerCreate, CareWorkerUpdate, Location
from typing import List
from src.utils.error_handling import AppException

router = APIRouter()

@router.post("/care-workers", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_worker(worker: CareWorkerCreate):
    return await CareWorkerService.create_care_worker(worker)

@router.get("/care-workers", response_model=List[CareWorker])
async def list_workers(status: CareWorkerStatus = None, skip: int = 0, limit: int = 100):
    return await CareWorkerService.list_care_workers(skip, limit)

@router.get("/care-workers/{worker_id}", response_model=CareWorker)
async def get_worker(worker_id: str):
    try:
        return await CareWorkerService.get_care_worker(worker_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/care-workers/{worker_id}", response_model=CareWorker)
async def update_worker(worker_id: str, worker: CareWorkerUpdate):
    try:
        return await CareWorkerService.update_care_worker(worker_id, worker)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.delete("/care-workers/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker(worker_id: str):
    success = await CareWorkerService.delete_care_worker(worker_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Care worker not found")

@router.put("/care-workers/{worker_id}/location", response_model=CareWorker)
async def update_worker_location(worker_id: str, location: Location):
    update_data = CareWorkerUpdate(current_location=location)
    try:
        return await CareWorkerService.update_care_worker(worker_id, update_data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
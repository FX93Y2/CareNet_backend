from fastapi import APIRouter, HTTPException, Depends, status
from src.services.care_worker_service import create_care_worker, get_care_workers, get_care_worker, update_care_worker, delete_care_worker
from src.models.schemas import CareWorker, CareWorkerStatus, CareWorkerCreate, CareWorkerUpdate, Location
from ..auth import get_current_user, User
from typing import List

router = APIRouter()

@router.post("/care-workers", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_worker(worker: CareWorkerCreate, current_user: User = Depends(get_current_user)):
    worker_id = await create_care_worker(worker.dict())
    return worker_id

@router.get("/care-workers", response_model=List[CareWorker])
async def list_workers(status: CareWorkerStatus = None, current_user: User = Depends(get_current_user)):
    return await get_care_workers(status)

@router.get("/care-workers/{worker_id}", response_model=CareWorker)
async def get_worker(worker_id: str, current_user: User = Depends(get_current_user)):
    worker = await get_care_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Care worker not found")
    return worker

@router.put("/care-workers/{worker_id}", response_model=CareWorker)
async def update_worker(worker_id: str, worker: CareWorkerUpdate, current_user: User = Depends(get_current_user)):
    updated_worker = await update_care_worker(worker_id, worker.dict(exclude_unset=True))
    if not updated_worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Care worker not found")
    return updated_worker

@router.delete("/care-workers/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker(worker_id: str, current_user: User = Depends(get_current_user)):
    success = await delete_care_worker(worker_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Care worker not found")

@router.put("/care-workers/{worker_id}/location", response_model=CareWorker)
async def update_worker_location(worker_id: str, location: Location, current_user: User = Depends(get_current_user)):
    updated_worker = await update_care_worker(worker_id, {"current_location": location.dict()})
    if not updated_worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Care worker not found")
    return updated_worker
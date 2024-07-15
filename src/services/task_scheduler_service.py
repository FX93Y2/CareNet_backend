from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from src.database.mongodb import get_database
from src.models.schemas import GasSensorData
from motor.motor_asyncio import AsyncIOMotorDatabase

app = FastAPI()

class Task(BaseModel):
    task_id: str
    sensor_id: str
    gas_level: float
    assigned_to: str
    status: str
    created_at: datetime
    updated_at: datetime

async def create_task(sensor_data: GasSensorData, db: AsyncIOMotorDatabase) -> str: # type: ignore
    task = Task(
        task_id=f"TASK_{sensor_data.sensor_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        sensor_id=sensor_data.sensor_id,
        gas_level=sensor_data.gas_level,
        assigned_to="",  # To be assigned
        status="PENDING",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    result = await db.tasks.insert_one(task.dict())
    return str(result.inserted_id)

async def assign_task_to_worker(task_id: str, worker_id: str, db: AsyncIOMotorDatabase): # type: ignore
    result = await db.tasks.update_one(
        {"task_id": task_id},
        {"$set": {"assigned_to": worker_id, "status": "ASSIGNED", "updated_at": datetime.now()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found or already assigned")

async def process_sensor_data(sensor_data: GasSensorData, background_tasks: BackgroundTasks):
    db = await get_database()
    if sensor_data.gas_level > 5.0:  # Threshold for task creation
        task_id = await create_task(sensor_data, db)
        background_tasks.add_task(assign_task_to_worker, task_id, "available_worker_id", db)

@app.post("/process-sensor-data")
async def process_data(sensor_data: GasSensorData, background_tasks: BackgroundTasks):
    await process_sensor_data(sensor_data, background_tasks)
    return {"status": "Data processed successfully"}

@app.get("/tasks/{worker_id}")
async def get_worker_tasks(worker_id: str):
    db = await get_database()
    tasks = await db.tasks.find({"assigned_to": worker_id}).to_list(length=100)
    return {"tasks": tasks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
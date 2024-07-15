from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.database.mongodb import get_database
from src.models.schemas import GasSensorData

app = FastAPI()

class SensorDataInput(BaseModel):
    sensor_id: str
    gas_level: float
    timestamp: datetime

@app.post("/ingest")
async def ingest_sensor_data(data: SensorDataInput):
    try:
        db = get_database()
        sensor_data = GasSensorData(
            sensor_id=data.sensor_id,
            gas_level=data.gas_level,
            timestamp=data.timestamp
        )
        result = await db.gas_sensor_data.insert_one(sensor_data.dict())
        
        if result.inserted_id:
            return {"status": "success", "message": "Data ingested successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to ingest data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
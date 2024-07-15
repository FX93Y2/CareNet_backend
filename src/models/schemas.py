from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class GasSensorData(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    sensor_id: str
    gas_level: float
    timestamp: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "sensor_id": "sensor_001",
                "gas_level": 1.23,
                "timestamp": "2023-07-15T12:34:56"
            }
        }
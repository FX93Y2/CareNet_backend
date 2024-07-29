from enum import Enum
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, EmailStr, Config as ConfigDict
from pydantic_core import core_schema
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.no_info_plain_validator_function(cls.validate)
        ])

class BaseMongoModel(BaseModel):
    class Config(ConfigDict):
        arbitrary_types_allowed = True
        populate_by_name = True

class ServiceType(str, Enum):
    MEDICAL_CHECKUP = "Medical Checkup" #医疗检查
    MEDICATION_ADMINISTRATION = "Medication Administration" #药物管理
    PHYSICAL_THERAPY = "Physical Therapy" #身体检查
    PERSONAL_CARE = "Personal Care" #个人护理（洗澡、洗头、换衣服等）

class UrgencyLevel(str, Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    EMERGENCY = "Emergency"

class Location(BaseModel):
    latitude: float
    longitude: float

# CareRequest models
class CareRequestBase(BaseMongoModel):
    client_id: PyObjectId
    service_type: ServiceType
    urgency: UrgencyLevel
    location: Location
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class CareRequestStatus(str, Enum):
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class CareRequest(CareRequestBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: CareRequestStatus = CareRequestStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_worker_id: Optional[PyObjectId] = None
    estimated_fee: Optional[float] = None

class CareRequestCreate(CareRequestBase):
    pass

class CareRequestUpdate(BaseMongoModel):
    status: Optional[CareRequestStatus] = None
    assigned_worker_id: Optional[PyObjectId] = None
    estimated_fee: Optional[float] = None

class CareCenter(BaseMongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    location: Location
    service_area: Dict[str, Any]

class CareCenterCreate(BaseModel):
    name: str
    location: Location
    service_area: List[Location]

class CareCenterUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[Location] = None
    service_area: Optional[List[Location]] = None

# Carewroker models

class CareWorkerBase(BaseMongoModel):
    name: str
    email: EmailStr
    phone_number: str
    specializations: List[ServiceType]
    care_center_id: PyObjectId
    current_location: Location

class CareWorkerStatus(str, Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    OFFLINE = "Offline"

class CareWorkerCreate(CareWorkerBase):
    password: str

class CareWorkerUpdate(BaseMongoModel):
    current_location: Optional[Location] = None
    status: Optional[CareWorkerStatus] = None

class CareWorker(CareWorkerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: CareWorkerStatus = CareWorkerStatus.AVAILABLE
    rating: float = Field(ge=0, le=5, default=0)
    completed_tasks: int = 0

# User models
class UserBase(BaseMongoModel):
    username: str
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    disabled: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
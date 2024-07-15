from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.utils.config import get_settings
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None # type: ignore
    db: Optional[AsyncIOMotorDatabase] = None # type: ignore

db = Database()

async def get_database() -> AsyncIOMotorDatabase: # type: ignore
    return db.db

async def connect_to_mongo():
    settings = get_settings()
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.db = db.client[settings.db_name]
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client is not None:
        db.client.close()
        print("Closed MongoDB connection")
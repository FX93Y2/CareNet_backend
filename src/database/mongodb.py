from motor.motor_asyncio import AsyncIOMotorClient
from src.utils.config import get_settings

settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None # type: ignore

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")

async def get_database():
    if not db.client:
        await connect_to_mongo()
    return db.client[settings.db_name]

async def get_collection(collection_name: str):
    database = await get_database()
    return database[collection_name]

async def get_care_requests_collection():
    return await get_collection("care_requests")

async def get_care_workers_collection():
    return await get_collection("care_workers")

async def get_users_collection():
    return await get_collection("users")
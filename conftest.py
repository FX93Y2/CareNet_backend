import sys
from pathlib import Path
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from src.database.mongodb import Database, db

# Get the absolute path of the project root
root_dir = Path(__file__).parent.absolute()

# Add the project root to the Python path
sys.path.insert(0, str(root_dir))

@pytest.fixture(autouse=True)
def mock_db_connection(monkeypatch):
    async def mock_get_database():
        return AsyncIOMotorClient().test_database
    
    monkeypatch.setattr(Database, "client", AsyncIOMotorClient())
    monkeypatch.setattr("src.database.mongodb.get_database", mock_get_database)
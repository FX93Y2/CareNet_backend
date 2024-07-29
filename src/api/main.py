'''main FASTAPI application file'''
from fastapi import FastAPI
from contextlib import asynccontextmanager

from . import auth
from .routes import care_requests, care_workers
from src.database.mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(care_requests.router, prefix="/api", tags=["Care Requests"])
app.include_router(care_workers.router, prefix="/api", tags=["Care Workers"])

@app.get("/")
async def root():
    return {"message": "Welcome to Fumicro Carenet API"}
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from .api.routes import care_requests, care_workers, care_centers
from .utils.error_handling import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    log_request
)
from .database.mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(title="CareNet API", lifespan=lifespan)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Add middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    await log_request(request)
    response = await call_next(request)
    return response

# Include routers
app.include_router(care_requests.router, prefix="/api/v1/care-requests", tags=["Care Requests"])
app.include_router(care_workers.router, prefix="/api/v1/care-workers", tags=["Care Workers"])
app.include_router(care_centers.router, prefix="/api/v1/care-centers", tags=["Care Centers"])

@app.get("/")
async def root():
    return {"message": "Welcome to Fumicro Carenet API"}

@app.get("/base_url")
async def get_base_url(request: Request):
    return {"base_url": str(request.base_url)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
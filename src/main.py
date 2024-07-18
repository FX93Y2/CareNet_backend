# src/main.py

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from api.routes import care_requests, auth
from utils.error_handling import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    log_request
)

app = FastAPI(title="FuMicroCareNet API")

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
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(care_requests.router, prefix="/api/v1", tags=["care requests"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from src.api.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash
)
from src.models.schemas import User, UserCreate, Token
from src.database.mongodb import get_users_collection
from src.utils.config import get_settings

settings = get_settings()

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route to get an access token."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    """Register a new user."""
    users_collection = await get_users_collection()
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    new_user = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": new_user.inserted_id})
    return User(**created_user)

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get the current user's information."""
    return current_user
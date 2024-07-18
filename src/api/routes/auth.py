from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from api.auth import create_access_token

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Here you would typically verify the username and password against your database
    # For this example, we'll just check if the username is "test" and password is "test"
    if form_data.username != "test" or form_data.password != "test":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"sub": form_data.username, "scopes": form_data.scopes}
    )
    return {"access_token": access_token, "token_type": "bearer"}
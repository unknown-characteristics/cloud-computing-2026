from fastapi import APIRouter, status, Depends, Response
from sqlalchemy.orm import Session
from dtos.user_dto import UserRegister, UserLogin, UserResponse
from service import user_service
from core.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    return user_service.register_new_user(user, db)

@router.post("/login")
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    token = user_service.authenticate_user(user, db)
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,  
        secure=True,   
        samesite="lax", 
        max_age=3600
    )
    
    return {"message": "Login successful"}
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dtos.user_dto import UserRegister, UserLogin, UserResponse
from repository import user_repo
from core import security

def register_new_user(user_in: UserRegister, db: Session) -> UserResponse:
    if user_repo.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = security.get_password_hash(user_in.password)
    user_data = {
        "name": user_in.name,
        "email": user_in.email,
        "hashed_password": hashed_pwd,
        "credibility_score": 1
    }

    db_user = user_repo.create_user(db, user_data)

    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        credibility_score=db_user.credibility_score
    )

def authenticate_user(user_in: UserLogin, db: Session) -> str:
    user = user_repo.get_user_by_email(db, user_in.email)
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token_data = {"sub": str(user.id)}
    token = security.create_access_token(token_data)
    
    return token
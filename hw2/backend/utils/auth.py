from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import select

from datetime import datetime, timedelta, timezone

from utils.settings import Settings
from utils.database import get_db
from models.user import User
from enums.role import RoleEnum

settings = Settings()

pass_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer("users/login")

def hash_password(password: str) -> str:
    return pass_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pass_context.verify(plain, hashed)

def create_token(id: int, role: RoleEnum, contestant_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    data = {"sub": str(id), "role": role.value, "exp": expire, "contestant_id": contestant_id}

    return jwt.encode(data, settings.JWT_KEY, "HS256")

def decode_token(token: str) -> str:
    return jwt.decode(token, settings.JWT_KEY, "HS256")

def authenticate_user(db: Session, username: str, password: str):
    user = db.execute(select(User).filter(User.username == username)).first()

    if not user or not verify_password(password, user[0].pwhash):
        return None
    
    return user[0]

def get_authenticated_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        id = payload["sub"]

        if id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    user = db.execute(select(User).filter(User.id == id)).first()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid logged in user")
    
    return user[0]

def check_admin_or_id_and_get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), id: int = -1, is_contestant_id: bool = False):
    payload = decode_token(token)
    if payload["role"] != RoleEnum.admin.value and (id == -1 or id != int(payload["sub" if not is_contestant_id else "contestant_id"])):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Must have admin role")
    
    if db is None:
        return None

    return get_authenticated_user(token, db)

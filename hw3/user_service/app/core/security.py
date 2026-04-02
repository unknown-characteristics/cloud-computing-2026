import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from helpers.settings import settings
from helpers.secrets import get_secret_data
import os

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({
        "iat": datetime.now(timezone.utc),
        "exp": expire, 
        "aud": settings.project_id, 
        "iss": os.environ.get("SERVICE_URL")
    })
    
    private_key = get_secret_data(settings.secret_key_name + "_PRIVATE")
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.algorithm, headers={"kid": "jwtkey"})
    return encoded_jwt

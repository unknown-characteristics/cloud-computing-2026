import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from helpers.settings import settings
from helpers.secrets import get_secret_data


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update(
        {
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
            "aud": settings.jwt_audience,
            "iss": os.environ.get("SERVICE_URL", "users-service"),
        }
    )

    private_key = get_secret_data(settings.secret_key_name + "-PRIVATE")
    return jwt.encode(
        to_encode,
        private_key,
        algorithm=settings.algorithm,
        headers={"kid": "jwtkey"},
    )

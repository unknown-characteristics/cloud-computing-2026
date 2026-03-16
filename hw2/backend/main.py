from fastapi import FastAPI, HTTPException, status, Request
from jose import JWTError, ExpiredSignatureError
import uvicorn
from contextlib import asynccontextmanager
from utils.database import engine, Base, SessionGenerator
from sqlalchemy.exc import DatabaseError

from controllers import users, contestants, contests, participations, prizes
from dtos.users import CreateUser
from models.user import User, RoleEnum
from utils.settings import settings

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionGenerator()
    existing = db.query(User).filter(User.username == "admin").first()
    if existing is None:
        create_user = CreateUser(username="admin", name="admin", email="admin@contrest.org", school="none", password=settings.DEFAULT_ADMIN_PASSWORD)
        await users.helper_create_user(create_user, RoleEnum.admin, db)
    db.close()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(prizes.router)
app.include_router(participations.router)
app.include_router(contestants.router)
app.include_router(contests.router)

@app.exception_handler(JWTError)
async def handle_jwt_error(request: Request, exc: JWTError):
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

@app.exception_handler(ExpiredSignatureError)
async def handle_expired_jwt(request: Request, exc: ExpiredSignatureError):
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Expired token")

@app.exception_handler(DatabaseError)
async def handle_database_error(request: Request, exc: DatabaseError):
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown database error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5014)

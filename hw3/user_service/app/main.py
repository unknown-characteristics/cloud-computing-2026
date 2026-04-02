from fastapi import FastAPI

from api.user_controller import router as user_router
from core.database import engine, Base

# create database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# user endpoints 
app.include_router(user_router)

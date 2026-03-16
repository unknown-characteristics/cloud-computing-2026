from fastapi import APIRouter, HTTPException, Body, Depends, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from httpx import AsyncClient

from dtos import users, contestants
from models.user import User
from enums.role import RoleEnum
from utils.database import get_db
from utils.settings import settings
from utils.email import is_valid_email

from utils import auth

from fastapi.routing import APIRoute

class CustomUsersRoute(APIRoute):
    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_handler(request):
            try:
                return await original_handler(request)
            except IntegrityError as e:
                msg = str(e.orig).lower()

                if "unique" in msg:
                    if "username" in msg:
                        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
                    elif "email" in msg:
                        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")

                print(f"Unknown users error: {e}")
                raise e

        return custom_handler

router = APIRouter(route_class=CustomUsersRoute)

async def helper_create_user(create_user: users.CreateUser, role: RoleEnum, db: Session):
    if not is_valid_email(create_user.email):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid email")

    existing = db.execute(select(User).filter(User.username == create_user.username)).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    
    contestant_create = contestants.CreateContestant(name=create_user.name, school=create_user.school)
    async with AsyncClient() as client:
        response = await client.post(f"http://{settings.CONTREST_URL}/contestants", json=contestant_create.model_dump())
        if response.status_code == 500:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Couldn't create contestant")
        
        if response.status_code != 201:
            return PlainTextResponse(response.json(), response.status_code)

    contestant = contestants.GetContestant.model_validate(response.json())

    user = User()
    user.username = create_user.username
    user.email = create_user.email
    user.contestant_id = contestant.id
    user.role = role
    user.pwhash = auth.hash_password(create_user.password)

    try:
        db.add(user)
        db.commit()
    except IntegrityError as e:
        db.rollback()

        async with AsyncClient() as client:
            response = await client.delete(f"http://{settings.CONTREST_URL}/contestants/{contestant.id}")

        raise e

    db.refresh(user)

    return user

@router.post("/users/register", response_model=users.GetUser)
async def register_user(create_user: users.CreateUser = Body(), db: Session = Depends(get_db)):
    user = await helper_create_user(create_user, RoleEnum.contestant, db)

    return JSONResponse(users.GetUser.model_validate(user, from_attributes=True).model_dump(), 201, headers={"Location": f"/users/{user.id}"})

@router.post("/users/login")
async def login_user(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    
    access_token = auth.create_token(user.id, user.role, user.contestant_id)
    return {"access_token": access_token}

@router.get("/users/me", response_model=users.GetUser)
async def get_current_user(user: User = Depends(auth.get_authenticated_user)):
    return user

@router.get("/users", response_model=list[users.GetUser])
async def get_users(current_user: User = Depends(auth.check_admin_or_id_and_get_user), db: Session = Depends(get_db)):
    result = [r[0] for r in db.execute(select(User)).all()]
    return result

@router.get("/users/{id}", response_model=users.GetUser)
async def get_user_by_id(id: int, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    user = auth.check_admin_or_id_and_get_user(token, db, id)

    if id == user.id:
        return user
    
    result = db.execute(select(User).filter(User.id == id)).first()
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return result[0]

@router.delete("/users/{id}")
async def delete_user_by_id(id: int, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    user = auth.check_admin_or_id_and_get_user(token, db, id)
    
    if user.id == id:
        deleted_user = user
    else:
        try:
            deleted_user = db.execute(select(User).filter(User.id == id)).first()[0]
        except TypeError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
    
    if deleted_user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ID not found")

    if deleted_user.username == "admin":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Can't delete main admin user")

    db.delete(deleted_user)
    async with AsyncClient() as client:
        response = await client.delete(f"http://{settings.CONTREST_URL}/contestants/{deleted_user.contestant_id}")
        if response.status_code != 204 and response.status_code != 404:
            db.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Couldn't delete user")
    
    db.commit()
    return PlainTextResponse("", status.HTTP_204_NO_CONTENT)

@router.put("/users/{id}", response_model=users.GetUser)
async def put_user(id: int, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db), modify_user: users.ModifyUser = Body()):
    user = auth.check_admin_or_id_and_get_user(token, db, id)

    if user.role != RoleEnum.admin and modify_user.role == RoleEnum.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot change role to admin")

    if user.id == id:
        modified_user = user
    else:
        try:
            modified_user = db.execute(select(User).filter(User.id == id)).first()[0]
        except TypeError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
    
    if modified_user.username == "admin" and modify_user.username != "admin":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot change username of admin")
    modified_user.username = modify_user.username
    
    if modified_user.email != modify_user.email and not is_valid_email(modify_user.email):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid email")
    modified_user.email = modify_user.email

    modified_user.pwhash = auth.hash_password(modify_user.password)

    if user.role != RoleEnum.admin and modify_user.role == RoleEnum.admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot change role to admin")
    if modify_user.role != RoleEnum.admin and modified_user.username == "admin":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot change role of main admin user")
    modified_user.role = modify_user.role

    db.commit()
    db.refresh(modified_user)

    return modified_user

@router.patch("/users/{id}", response_model=users.GetUser)
async def patch_user(id: int, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db), update_user: users.UpdateUser = Body()):
    user = auth.check_admin_or_id_and_get_user(token, db, id)

    if user.id == id:
        modified_user = user
    else:
        try:
            modified_user = db.execute(select(User).filter(User.id == id)).first()[0]
        except TypeError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

    if update_user.username != None:
        if modified_user.username == "admin" and update_user.username != "admin":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot change username of admin")

        modified_user.username = update_user.username
    
    if update_user.email != None:
        if modified_user.email != update_user.email and not is_valid_email(update_user.email):
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid email")
        modified_user.email = update_user.email

    if update_user.password != None:
        modified_user.pwhash = auth.hash_password(update_user.password)

    if update_user.role != None:
        if user.role != RoleEnum.admin and update_user.role == RoleEnum.admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot change role to admin")
        
        if update_user.role != RoleEnum.admin and modified_user.username == "admin":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot change role of main admin user")

        modified_user.role = update_user.role

    db.commit()
    db.refresh(modified_user)

    return modified_user

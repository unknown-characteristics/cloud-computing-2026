from fastapi import HTTPException
from sqlalchemy.orm import Session
from dtos.user_dto import UserRegister, UserLogin, UserResponse
from repository import user_repo, outbox_repository, other_event_repository
from core import security
from model.outbox import OutboxEvent
from service.outbox_service import OutboxService
import json, uuid

def register_new_user(user_in: UserRegister, db: Session) -> UserResponse:
    with db.begin():
        if user_repo.get_user_by_email(db, user_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pwd = security.get_password_hash(user_in.password)
        user_data = {
            "name": user_in.name,
            "email": user_in.email,
            "hashed_password": hashed_pwd,
            "credibility_score": 1,
            "created_assignments_count": 0
        }

        db_user = user_repo.create_user(db, user_data)
        db.refresh(db_user)
        event_data = json.dumps({"name": db_user.name, "id": db_user.id}).encode("utf-8")
        event_id = f"users-event-" + uuid.uuid4().hex
        event_type = "user.created"
        event = OutboxEvent(event_id=event_id, event_type=event_type, data=event_data)
        outbox_repository.OutboxRepository(db).create(event)

    OutboxService(db).process_pending_events()
    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        credibility_score=db_user.credibility_score,
        created_assignments_count=db_user.created_assignments_count
    )

def delete_user(user_id: int, db: Session):
    with db.begin():
        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="ID not found")

        event_data = json.dumps({"name": user.name, "id": user.id}).encode("utf-8")
        event_id = f"users-event-" + uuid.uuid4().hex
        event_type = "user.deleted"
        event = OutboxEvent(event_id=event_id, event_type=event_type, data=event_data)

        user_repo.delete_user(db, user)
        outbox_repository.OutboxRepository(db).create(event)
    
    OutboxService(db).process_pending_events()

def change_user_assignment_count(user_id: int, db: Session, event_id: str, increment: bool):
    other_repo = other_event_repository.OtherEventRepository(db)
    with db.begin():
        if other_repo.exists(event_id):
            return
        
        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            # raise HTTPException(status_code=404, detail="ID not found")
            return

        user.created_assignments_count += 1 if increment else -1
        other_repo.create(event_id)

def authenticate_user(user_in: UserLogin, db: Session) -> str:
    user = user_repo.get_user_by_email(db, user_in.email)
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token_data = {"sub": json.dumps({"id": user.id, "name": str(user.name), "email": str(user.email), "created_assignments_count": str(user.created_assignments_count), "credibility_score": str(user.credibility_score)})}
    token = security.create_access_token(token_data)
    
    return token

def get_user_by_id(user_id: int, db: Session):
    db_user = user_repo.get_user_by_id(db, user_id)
    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        credibility_score=db_user.credibility_score,
        created_assignments_count=db_user.created_assignments_count
    )

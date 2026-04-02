from sqlalchemy.orm import Session
from model.user_model import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def create_user(db: Session, user_data: dict) -> User:
    db_user = User(**user_data)
    db.add(db_user)
    db.flush()
    # db.commit()
    # db.refresh(db_user)
    return db_user

def delete_user(db: Session, user: User):
    db.delete(user)

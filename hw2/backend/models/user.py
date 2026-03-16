from sqlalchemy import Column, Integer, String, Enum, Boolean
from utils.database import Base
from enums.role import RoleEnum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    contestant_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    pwhash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, index=True)

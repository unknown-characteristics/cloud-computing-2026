from sqlalchemy import Column, Integer, String
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)        
    email = Column(String(255), unique=True, index=True, nullable=False) 
    hashed_password = Column(String(255), nullable=False)
    credibility_score = Column(Integer, default=1)
    created_assignments_count = Column(Integer, nullable=False, default=0)

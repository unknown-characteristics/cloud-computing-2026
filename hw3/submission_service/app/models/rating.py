from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Rating(BaseModel):
    id: Optional[str] = None
    user_id: int
    submission_id: str
    assignment_id: int
    score: int
    comment: Optional[str] = None
    status: str = "active"  # Pentru soft-delete la rating
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Submission(BaseModel):
    id: Optional[str] = None
    user_id: int
    assignment_id: str
    filepath: str
    status: str = "active" # poate fi 'active' sau 'deleted' (soft delete)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Assignment(BaseModel):
    """
    Mirrors the Datastore 'assignments' kind schema.
    """
    id: Optional[int | str] = None                        # Datastore document ID (auto-generated)
    created_at: Optional[datetime] = None
    creator_id: int
    description: str
    name: str
    status: str
    start_time: datetime
    stop_grade_time: datetime
    stop_submit_time: datetime
    submission_count: int = 0
    type: str
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CreateSubmissionDTO(BaseModel):
    user_id: int | None = None
    assignment_id: int
    filepath: str

class UpdateSubmissionDTO(BaseModel):
    filepath: Optional[str] = None

class SubmissionResponseDTO(BaseModel):
    id: str | int
    user_id: int
    assignment_id: int
    filepath: str
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
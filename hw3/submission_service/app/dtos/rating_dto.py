from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CreateRatingDTO(BaseModel):
    submission_id: int
    assignment_id: int
    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class UpdateRatingDTO(BaseModel):
    score: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class RatingResponseDTO(BaseModel):
    id: int
    user_id: int
    submission_id: int
    assignment_id: int
    score: int
    comment: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CreateRatingDTO(BaseModel):
    user_id: int
    submission_id: str
    assignment_id: str
    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class UpdateRatingDTO(BaseModel):
    score: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class RatingResponseDTO(BaseModel):
    id: str
    user_id: int
    submission_id: str
    assignment_id: str
    score: int
    comment: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
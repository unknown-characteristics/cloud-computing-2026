from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreateAssignmentDTO(BaseModel):
    creator_id: int | None = None
    description: str
    name: str
    start_time: datetime
    stop_grade_time: datetime
    stop_submit_time: datetime
    type: str

    class Config:
        json_schema_extra = {
            "example": {
                "creator_id": 1,
                "description": "Complete the following exercises.",
                "name": "Week 1 Assignment",
                "start_time": "2024-09-01T08:00:00",
                "stop_grade_time": "2024-09-10T23:59:59",
                "stop_submit_time": "2024-09-08T23:59:59",
                "type": "homework",
            }
        }


class EditAssignmentDTO(BaseModel):
    description: Optional[str] = None
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    stop_grade_time: Optional[datetime] = None
    stop_submit_time: Optional[datetime] = None
    type: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Week 1 Assignment (Updated)",
                "stop_submit_time": "2024-09-09T23:59:59",
            }
        }


class AssignmentResponseDTO(BaseModel):
    id: str | int
    creator_id: int
    description: str
    name: str
    start_time: datetime
    stop_grade_time: datetime
    stop_submit_time: datetime
    submission_count: int
    type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LeaderboardEntryDTO(BaseModel):
    assignment_id: str | int
    name: str
    submission_count: int
    rank: int


class LeaderboardResponseDTO(BaseModel):
    entries: list[LeaderboardEntryDTO]
    total: int

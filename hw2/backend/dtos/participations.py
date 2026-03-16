from pydantic import BaseModel
import datetime

class CreateParticipation(BaseModel):
    contest_id: int | None = None
    contestant_id: int | None = None
    answer: str | None
    score: float | None = None

class GetParticipation(BaseModel):
    contest_id: int
    contestant_id: int
    answer: str | None
    join_time: datetime.datetime
    submission_time: datetime.datetime | None
    score: float

class ModifyParticipation(BaseModel):
    answer: str | None
    score: float | None = None

class UpdateParticipation(BaseModel):
    answer: str | None = None
    score: float | None = None

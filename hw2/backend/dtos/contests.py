from pydantic import BaseModel
from enums.status import StatusEnum
import datetime

class CreateContest(BaseModel):
    name: str
    difficulty: float
    hint: str | None = None
    solution: str
    status: StatusEnum | None = None

class GetContest(BaseModel):
    id: int
    name: str
    hint: str
    difficulty: float
    solution: str
    start_time: datetime.datetime
    end_time: datetime.datetime | None
    status: StatusEnum

class ModifyContest(BaseModel):
    name: str
    difficulty: float
    hint: str
    solution: str
    status: StatusEnum

class UpdateContest(BaseModel):
    name: str | None = None
    difficulty: float | None = None
    hint: str | None = None
    solution: str | None = None
    status: StatusEnum | None = None

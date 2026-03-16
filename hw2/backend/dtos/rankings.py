from pydantic import BaseModel
import datetime

class GetRanking(BaseModel):
    rank: int
    contestant_id: int
    submission_time: datetime.datetime
    award_id: int | None
    score: float
    answer: str

import datetime

# not an actual table, closer to a view
class Ranking:
    rank: int
    contestant_id: int
    submission_time: datetime.datetime
    award_id: int
    score: float
    answer: str

    @staticmethod
    def get_lowercase_columns():
        return ["rank", "contestant_id", "submission_time", "award_id", "score", "answer"]

    def from_full_tuple(self, tuple):
        self.rank = tuple[0]
        self.contestant_id = tuple[1]
        self.submission_time = tuple[2]
        self.award_id = tuple[3]
        self.score = tuple[4]
        self.answer = tuple[5]

        return self

    def as_dict(self):
        return {"rank": self.rank, "contestant_id": self.contestant_id, "submission_time": self.submission_time.isoformat(), "award_id": self.award_id, "score": self.score, "answer": self.answer}

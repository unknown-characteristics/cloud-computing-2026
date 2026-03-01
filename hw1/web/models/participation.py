import datetime

class Participation:
    contest_id: int
    contestant_id: int
    answer: str
    join_time: datetime.datetime
    submission_time: datetime.datetime

    @staticmethod
    def get_table_name() -> str:
        return "SUBMISSIONS"

    @staticmethod
    def get_lowercase_columns() -> set[str]:
        return ["contest_id", "contestant_id", "answer", "join_time", "submission_time"]
    
    def from_full_tuple(self, tuple):
        self.contest_id = tuple[0]
        self.contestant_id = tuple[1]
        self.answer = tuple[2]
        self.join_time = tuple[3]
        self.submission_time = tuple[4]

        return self

    def as_dict(self):
        return {"contest_id": self.contest_id, "contestant_id": self.contestant_id, "answer": self.answer, "join_time": self.join_time.isoformat(), "submission_time": self.submission_time.isoformat()}

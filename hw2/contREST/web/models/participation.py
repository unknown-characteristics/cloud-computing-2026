import datetime

class Participation:
    contest_id: int
    contestant_id: int
    answer: str
    score: float
    join_time: datetime.datetime
    submission_time: datetime.datetime | None

    @staticmethod
    def get_table_name() -> str:
        return "SUBMISSIONS"

    @staticmethod
    def get_lowercase_columns() -> list[str]:
        return ["contest_id", "contestant_id", "answer", "score", "join_time", "submission_time"]
    
    @staticmethod
    def simplify_integrity_error_message(code, message):
        if "C_SUBM_FK_CONTEST_ID" in message and "parent key not found" in message:
            return 422, "Contest ID was not found"
        elif "C_SUBM_FK_CONTESTANT_ID" in message and "parent key not found" in message:
            return 422, "Contestant ID was not found"
        elif "C_SUBM_PK_CONTEST_CONTESTANT_ID" in message:
            return 409, "Contestant is already participating in the contest"
        elif "cannot insert NULL into" in message or "to NULL" in message:
            if "score" in message or "SCORE" in message:
                return 422, "Score may not be NULL"
            else:
                return 422, "ID may not be NULL"
        elif code == 20002:
            return 409, "Cannot join/submit contest after contest has ended"
        else:
            return 500, "Unknown database error"

    def from_full_tuple(self, tuple):
        self.contest_id = tuple[0]
        self.contestant_id = tuple[1]
        self.answer = tuple[2]
        self.score = tuple[3]
        self.join_time = tuple[4]
        self.submission_time = tuple[5]

        return self

    def as_dict(self):
        return {"contest_id": self.contest_id, "contestant_id": self.contestant_id, "answer": self.answer, "score": self.score, "join_time": self.join_time.isoformat(), "submission_time": None if self.submission_time == None else self.submission_time.isoformat()}

import datetime

class Contest:
    id: int
    name: str
    difficulty: float
    solution: str
    start_time: datetime.datetime
    end_time: datetime.datetime | None
    status: str

    @staticmethod
    def get_table_name() -> str:
        return "CONTESTS"

    @staticmethod
    def get_lowercase_columns() -> set[str]:
        return ["id", "name", "difficulty", "solution", "start_time", "end_time", "status"]
    
    def from_full_tuple(self, tuple):
        self.id = tuple[0]
        self.name = tuple[1]
        self.difficulty = tuple[2]
        self.solution = tuple[3]
        self.start_time = tuple[4]
        self.end_time = tuple[5]
        self.status = tuple[6]

        return self

    def as_dict(self):
        return {"id": self.id, "name": self.name, "difficulty": self.difficulty, "solution": self.solution, "start_time": self.start_time.isoformat(), "end_time": None if self.end_time == None else self.end_time.isoformat(), "status": self.status}
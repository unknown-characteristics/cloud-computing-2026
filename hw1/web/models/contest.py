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
    def get_lowercase_columns() -> list[str]:
        return ["id", "name", "difficulty", "solution", "start_time", "end_time", "status"]

    @staticmethod
    def simplify_integrity_error_message(code, message):
        if "C_CONTESTS_VALID_STATUS" in message and "parent key not found" in message:
            return 422, "Invalid status (must be 'active' or)"
        elif "unique" in message and "NAME" in message:
            return 409, "Another contest has the same name"
        elif "cannot insert NULL into" in message or "to NULL" in message:
            if "NAME" in message:
                return 422, "Name may not be NULL"
            elif "DIFFICULTY" in message:
                return 422, "Difficulty may not be NULL"
            elif "SOLUTION" in message:
                return 422, "Solution may not be NULL"
            elif "STATUS" in message:
                return 422, "Status may not be NULL"
            else:
                return 422, "Cannot insert NULL"
        elif code == 20202:
            return 409, "Cannot modify contest after ending it"
        else:
            return 500, "Unknown database error"

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
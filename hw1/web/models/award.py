class Award:
    contest_id: int
    prize_id: int
    contestant_id: int

    @staticmethod
    def get_table_name() -> str:
        return "AWARDS"

    @staticmethod
    def get_lowercase_columns() -> set[str]:
        return ["contest_id", "prize_id", "contestant_id"]
    
    def from_full_tuple(self, tuple):
        self.contest_id = tuple[0]
        self.prize_id = tuple[1]
        self.contestant_id = tuple[2]

        return self

    def as_dict(self):
        return {"contest_id": self.contest_id, "prize_id": self.prize_id, "contestant_id": self.contestant_id}

class Award:
    contest_id: int
    prize_id: int
    contestant_id: int

    @staticmethod
    def get_table_name() -> str:
        return "AWARDS"

    @staticmethod
    def get_lowercase_columns() -> list[str]:
        return ["contest_id", "prize_id", "contestant_id"]
    
    @staticmethod
    def simplify_integrity_error_message(code, message):
        if "C_AWARD_FK_CONTEST_PRIZE_ID" in message and "parent key not found" in message:
            return 422, "Contest or prize ID was not found"
        elif "C_AWARD_FK_CONTESTANT_ID" in message and "parent key not found" in message:
            return 422, "Contestant ID was not found"
        elif "C_AWARD_PK_ALL_IDS" in message:
            return 409, "Contestant already received the specified prize in the contest"
        elif "cannot insert NULL into" in message:
            return 422, "ID may not be NULL"
        else:
            return 500, "Unknown database error"

    def from_full_tuple(self, tuple):
        self.contest_id = tuple[0]
        self.prize_id = tuple[1]
        self.contestant_id = tuple[2]

        return self

    def as_dict(self):
        return {"contest_id": self.contest_id, "prize_id": self.prize_id, "contestant_id": self.contestant_id}

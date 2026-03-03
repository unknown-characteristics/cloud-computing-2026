class Prize:
    contest_id: int
    prize_id: int
    initial_qty: int
    remaining_qty: int
    description: str
    estimated_value: int

    @staticmethod
    def get_table_name() -> str:
        return "PRIZES"

    @staticmethod
    def get_lowercase_columns() -> list[str]:
        return ["contest_id", "prize_id", "initial_qty", "remaining_qty", "description", "estimated_value"]
    
    @staticmethod
    def simplify_integrity_error_message(code, message):
        if "C_PRIZE_FK_CONTEST_ID" in message and "parent key not found" in message:
            return 422, "Contest ID was not found"
        elif "cannot insert NULL into" in message or "to NULL" in message:
            if "INITIAL_QTY" in message:
                return 422, "Initial quantity may not be NULL"
            elif "DESCRIPTION" in message:
                return 422, "Description may not be NULL"
            elif "ESTIMATED_VALUE" in message:
                return 422, "Estimated value may not be NULL"
            else:
                return 422, "Cannot insert NULL"
        elif "C_PRIZE_REMAINING_VALID" in message:
            return 422, "Quantity may not be negative"
        elif code == 20003:
            return 409, "Cannot add/remove prizes after contest has ended"
        elif code == 20004:
            return 409, "Cannot modify prizes after contest has ended"
        else:
            return 500, "Unknown database error"

    def from_full_tuple(self, tuple):
        self.contest_id = tuple[0]
        self.prize_id = tuple[1]
        self.initial_qty = tuple[2]
        self.remaining_qty = tuple[3]
        self.description = tuple[4]
        self.estimated_value = tuple[5]

        return self

    def as_dict(self):
        return {"contest_id": self.contest_id, "prize_id": self.prize_id, "initial_qty": self.initial_qty, "remaining_qty": self.remaining_qty, "description": self.description, "estimated_value": self.estimated_value}

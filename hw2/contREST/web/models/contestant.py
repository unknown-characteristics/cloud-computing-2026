class Contestant:
    id: int
    name: str
    school: str

    @staticmethod
    def get_table_name() -> str:
        return "CONTESTANTS"

    @staticmethod
    def get_lowercase_columns() -> list[str]:
        return ["id", "name", "school"]
    
    @staticmethod
    def simplify_integrity_error_message(code, message):
        if "cannot insert NULL into" in message or "to NULL":
            if "NAME" in message:
                return 422, "Name may not be NULL"
            elif "SCHOOL" in message:
                return 422, "School may not be NULL"
            else:
                return 422, "Cannot insert NULL"
        else:
            return 500, "Unknown database error"

    def from_full_tuple(self, tuple):
        self.id = tuple[0]
        self.name = tuple[1]
        self.school = tuple[2]

        return self

    def as_dict(self):
        return {"id": self.id, "name": self.name, "school": self.school}

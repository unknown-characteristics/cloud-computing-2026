class Contestant:
    id: int
    name: str
    email: str
    school: str

    @staticmethod
    def get_table_name() -> str:
        return "CONTESTANTS"

    @staticmethod
    def get_lowercase_columns() -> set[str]:
        return ["id", "name", "email", "school"]
    
    @staticmethod
    def simplify_integrity_error_message(code, message):
        if "unique" in message and "EMAIL" in message:
            return "Another contestant has the same email"
        elif "cannot insert NULL into" in message or "to NULL":
            if "NAME" in message:
                return "Name may not be NULL"
            elif "SCHOOL" in message:
                return "School may not be NULL"
            elif "EMAIL" in message:
                return "Email may not be NULL"
            else:
                return "Cannot insert NULL"
        else:
            return "Unknown database error"

    def from_full_tuple(self, tuple):
        self.id = tuple[0]
        self.name = tuple[1]
        self.email = tuple[2]
        self.school = tuple[3]

        return self

    def as_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "school": self.school}

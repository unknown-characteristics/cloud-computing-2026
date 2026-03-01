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
    
    def from_full_tuple(self, tuple):
        self.id = tuple[0]
        self.name = tuple[1]
        self.email = tuple[2]
        self.school = tuple[3]

        return self

    def as_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "school": self.school}

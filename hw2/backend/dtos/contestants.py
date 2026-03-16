from pydantic import BaseModel

class CreateContestant(BaseModel):
    name: str
    school: str

class GetContestant(BaseModel):
    id: int
    name: str
    school: str

class ModifyContestant(BaseModel):
    name: str
    school: str

class UpdateContestant(BaseModel):
    name: str | None = None
    school: str | None = None

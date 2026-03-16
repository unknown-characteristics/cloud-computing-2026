from pydantic import BaseModel
from enums.role import RoleEnum

class CreateUser(BaseModel):
    username: str
    name: str
    email: str
    school: str
    password: str

class GetUser(BaseModel):
    id: int
    username: str
    email: str
    role: str
    contestant_id: int

    class Config:
        from_attributes = True
    
class ModifyUser(BaseModel):
    username: str
    email: str
    password: str
    role: RoleEnum

class UpdateUser(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    role: RoleEnum | None = None

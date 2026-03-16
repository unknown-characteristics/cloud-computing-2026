from pydantic import BaseModel

class PhotoModel(BaseModel):
    photo_url: str
    author_url: str
    author_name: str
    photo_page_url: str

class CreatePrize(BaseModel):
    initial_qty: int
    description: str
    estimated_value: int
    photo_data: PhotoModel | None = None

class GetPrize(BaseModel):
    contest_id: int
    prize_id: int
    initial_qty: int
    remaining_qty: int
    description: str
    estimated_value: int
    photo_data: PhotoModel | None

class ModifyPrize(BaseModel):
    initial_qty: int
    description: str
    estimated_value: int
    photo_data: PhotoModel | None

class UpdatePrize(BaseModel):
    initial_qty: int | None = None
    description: str | None = None
    estimated_value: int | None = None
    photo_data: PhotoModel | None

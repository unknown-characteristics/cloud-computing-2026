from fastapi import APIRouter, status
from app.dtos.rating_dto import CreateRatingDTO, UpdateRatingDTO, RatingResponseDTO
from app.service.rating_service import RatingService

router = APIRouter()
_service = RatingService()

@router.post("/", response_model=RatingResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(dto: CreateRatingDTO):
    return await _service.create(dto)

@router.get("/submission/{sub_id}", response_model=list[RatingResponseDTO])
async def get_by_sub(sub_id: str):
    return await _service.get_by_submission(sub_id)

@router.patch("/{rating_id}", response_model=RatingResponseDTO)
async def update(rating_id: str, dto: UpdateRatingDTO):
    return await _service.update(rating_id, dto)

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(rating_id: str):
    await _service.delete(rating_id)
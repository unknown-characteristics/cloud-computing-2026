from fastapi import APIRouter, status, Depends
from app.dtos.rating_dto import CreateRatingDTO, UpdateRatingDTO, RatingResponseDTO
from app.service.rating_service import RatingService
from app.api.dependencies import get_current_user_id

router = APIRouter()
_service = RatingService()

@router.post("/", response_model=RatingResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(dto: CreateRatingDTO, user_id: int = Depends(get_current_user_id)):
    return _service.create(dto, user_id)

@router.get("/submission/{sub_id}", response_model=list[RatingResponseDTO])
async def get_by_sub(sub_id: str, user_id: int = Depends(get_current_user_id)):
    return _service.get_by_submission(sub_id)

@router.patch("/{rating_id}", response_model=RatingResponseDTO)
async def update(rating_id: str, dto: UpdateRatingDTO, user_id: int = Depends(get_current_user_id)):
    return _service.update(rating_id, dto, user_id)

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(rating_id: str, user_id: int = Depends(get_current_user_id)):
    _service.delete(rating_id, user_id)
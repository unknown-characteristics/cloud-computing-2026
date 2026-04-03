from fastapi import APIRouter, status, Depends
from app.dtos.rating_dto import CreateRatingDTO, UpdateRatingDTO, RatingResponseDTO
from app.service.rating_service import RatingService
from app.helpers.user_helper import extract_user_token

router = APIRouter()
_service = RatingService()

@router.post("/", response_model=RatingResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(dto: CreateRatingDTO, user_token: dict = Depends(extract_user_token)):
    return _service.create(dto, user_token["sub"]["id"])

@router.get("/submission/{sub_id}", response_model=list[RatingResponseDTO])
async def get_by_sub(sub_id: int, user_token: dict = Depends(extract_user_token)):
    return _service.get_by_submission(sub_id, user_token["sub"]["id"])

@router.patch("/{rating_id}", response_model=RatingResponseDTO)
async def update(rating_id: str, dto: UpdateRatingDTO, user_token: dict = Depends(extract_user_token)):
    return _service.update(rating_id, dto, user_token["sub"]["id"])

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(rating_id: str, user_token: dict = Depends(extract_user_token)):
    _service.delete(rating_id, user_token["sub"]["id"])

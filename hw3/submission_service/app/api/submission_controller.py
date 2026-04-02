from fastapi import APIRouter, status, Depends, HTTPException
from app.dtos.submission_dto import CreateSubmissionDTO, UpdateSubmissionDTO, SubmissionResponseDTO
from app.service.submission_service import SubmissionService
from app.helpers.user_helper import extract_user_token

router = APIRouter()
_service = SubmissionService()

@router.post("/", response_model=SubmissionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(dto: CreateSubmissionDTO, user_token: dict | None = Depends(extract_user_token)):
    if not user_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in to perform this action")
    
    dto.user_id = user_token["sub"]
    return _service.create(dto)

@router.get("/assignment/{assignment_id}", response_model=list[SubmissionResponseDTO])
async def get_by_assignment(assignment_id: str):
    return _service.get_all_by_assignment(assignment_id)

@router.patch("/{sub_id}", response_model=SubmissionResponseDTO)
async def update(sub_id: str, dto: UpdateSubmissionDTO):
    return _service.update(sub_id, dto)

@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(sub_id: str):
    _service.delete(sub_id)
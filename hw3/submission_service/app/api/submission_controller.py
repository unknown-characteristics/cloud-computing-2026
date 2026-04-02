from fastapi import APIRouter, status
from app.dtos.submission_dto import CreateSubmissionDTO, UpdateSubmissionDTO, SubmissionResponseDTO
from app.service.submission_service import SubmissionService

router = APIRouter()
_service = SubmissionService()

@router.post("/", response_model=SubmissionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(dto: CreateSubmissionDTO):
    return await _service.create(dto)

@router.get("/assignment/{assignment_id}", response_model=list[SubmissionResponseDTO])
async def get_by_assignment(assignment_id: str):
    return await _service.get_all_by_assignment(assignment_id)

@router.patch("/{sub_id}", response_model=SubmissionResponseDTO)
async def update(sub_id: str, dto: UpdateSubmissionDTO):
    return await _service.update(sub_id, dto)

@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(sub_id: str):
    await _service.delete(sub_id)
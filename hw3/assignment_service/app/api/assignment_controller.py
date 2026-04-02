from fastapi import APIRouter, status, Depends, HTTPException
from app.helpers.user_helper import extract_user_token

from app.dtos.assignment_dto import (
    CreateAssignmentDTO,
    EditAssignmentDTO,
    AssignmentResponseDTO,
    LeaderboardResponseDTO,
)
from app.service.assignment_service import AssignmentService

router = APIRouter()
_service = AssignmentService()


@router.post(
    "/",
    response_model=AssignmentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assignment",
)
async def create_assignment(dto: CreateAssignmentDTO, user_token: dict | None = Depends(extract_user_token)) -> AssignmentResponseDTO:
    if not user_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in to perform this action")
    
    dto.creator_id = int(user_token["sub"])
    
    return _service.create_assignment(dto)


@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assignment by ID",
)
async def delete_assignment(assignment_id: str) -> None:
    _service.delete_assignment(assignment_id)


@router.get(
    "/",
    response_model=list[AssignmentResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get all assignments",
)
async def get_assignments() -> list[AssignmentResponseDTO]:
    return _service.get_assignments()


@router.patch(
    "/{assignment_id}",
    response_model=AssignmentResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Edit an existing assignment",
)
async def edit_assignment(assignment_id: str, dto: EditAssignmentDTO) -> AssignmentResponseDTO:
    return _service.edit_assignment(assignment_id, dto)


@router.get(
    "/deadline-reached",
    response_model=list[AssignmentResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get all assignments whose submission deadline has passed",
)
async def deadline_reached() -> list[AssignmentResponseDTO]:
    return _service.deadline_reached()


@router.get(
    "/leaderboard",
    response_model=LeaderboardResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get the assignment leaderboard ranked by submission count",
)
async def get_leaderboard() -> LeaderboardResponseDTO:
    return _service.get_leaderboard()

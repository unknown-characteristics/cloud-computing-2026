from app.repository.store_repository import StoreRepository
from fastapi import APIRouter, status, Depends, HTTPException
from app.helpers.user_helper import extract_user_token
from datetime import datetime, timezone
import json, uuid

from app.dtos.assignment_dto import (
    CreateAssignmentDTO,
    EditAssignmentDTO,
    AssignmentResponseDTO,
    # LeaderboardResponseDTO,
)
from app.models.assignment import CheckDeadlinePayload
from app.models.outbox import OutboxEvent
from app.service.assignment_service import AssignmentService
from app.service.outbox_service import OutboxService

router = APIRouter()
_service = AssignmentService()
_assignment_repo = StoreRepository()
 

# Status transitions per deadline type
_DEADLINE_STATUS: dict[str, str] = {
    "stop_submit": "closed",       # no more submissions accepted
    "stop_grade":  "graded",       # grading window is also over
}

@router.post(
    "/",
    response_model=AssignmentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assignment",
)
async def create_assignment(dto: CreateAssignmentDTO, user_token: dict | None = Depends(extract_user_token)) -> AssignmentResponseDTO:
    if not user_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You must be logged in to perform this action")
    
    dto.creator_id = int(user_token["sub"]["id"])
    
    return await _service.create_assignment(dto)


@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assignment by ID",
)
async def delete_assignment(assignment_id: str) -> None:
    await _service.delete_assignment(assignment_id)

@router.get(
    "/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Get an assignment by ID",
)
async def get_assignment_by_id(assignment_id: str) -> None:
    return _service.get_assignment_by_id(assignment_id)

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
    return await _service.edit_assignment(assignment_id, dto)

@router.post(
    "/check-deadline/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Called by Cloud Tasks when a deadline is reached",
)
async def check_deadline(assignment_id: str, payload: CheckDeadlinePayload) -> dict:
    print(f"CHECKING DEADLINE FOR {assignment_id}!!!")
    if payload.deadline_type not in _DEADLINE_STATUS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown deadline_type '{payload.deadline_type}'",
        )
 
    assignment = _assignment_repo.get_assignment_by_id(assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment {assignment_id} not found",
        )
 
    now = datetime.now(timezone.utc)
    new_status = _DEADLINE_STATUS[payload.deadline_type]
 
    # Guard: only transition forward (don't downgrade an already-graded assignment)
    status_order = ["active", "closed", "graded"]
    current_index = status_order.index(assignment.status) if assignment.status in status_order else -1
    new_index = status_order.index(new_status)
 
    if new_index <= current_index:
        # Already at or past this status — nothing to do, return 200 so Cloud Tasks won't retry
        return {"detail": "No status change needed", "current_status": assignment.status}
 
    # Update assignment status in Datastore
    updated = _assignment_repo.update_assignment(assignment_id, {"status": new_status})
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update assignment status",
        )

    await OutboxService().process_pending_events()
 
    return {
        "assignment_id": assignment_id,
        "deadline_type": payload.deadline_type,
        "old_status": assignment.status,
        "new_status": new_status,
    }

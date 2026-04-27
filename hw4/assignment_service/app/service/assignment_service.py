import json
import uuid

from fastapi import HTTPException, status

from app.dtos.assignment_dto import (
    CreateAssignmentDTO,
    EditAssignmentDTO,
    AssignmentResponseDTO,
    # LeaderboardEntryDTO,
    # LeaderboardResponseDTO,
)
from app.models.assignment import Assignment
from app.models.outbox import OutboxEvent
from app.repository.store_repository import StoreRepository
from app.helpers.datetime_helpers import is_past
from app.service.outbox_service import OutboxService
from app.core.datastore_client import get_datastore_client
from app.core.task_client import schedule_task

class AssignmentService:
    def __init__(self):
        self._repo = StoreRepository()
        self._client = get_datastore_client()

    async def create_assignment(self, dto: CreateAssignmentDTO) -> AssignmentResponseDTO:
        assignment = Assignment(**dto.model_dump())
        assignment.status = "active"
        id = str(uuid.uuid4())
        assignment.id = id
        # --- Schedule Cloud Tasks for the two deadlines ---
    
        # Task 1: fires at stop_submit_time
        await schedule_task(
            url_path=f"/assignments/check-deadline/{assignment.id}",
            payload={"deadline_type": "stop_submit"},
            schedule_time=assignment.stop_submit_time,
        )
    
        # Task 2: fires at stop_grade_time
        await schedule_task(
            url_path=f"/assignments/check-deadline/{assignment.id}",
            payload={"deadline_type": "stop_grade"},
            schedule_time=assignment.stop_grade_time,
        )

        assignment = self._repo.create_with_outbox(id, assignment)
        
        await OutboxService().process_pending_events()

        return self._to_response(assignment)
    
    async def delete_assignment(self, assignment_id: int) -> None:
        self._repo.delete_with_outbox(assignment_id)
        await OutboxService().process_pending_events()

    def get_assignments(self) -> list[AssignmentResponseDTO]:
        assignments = self._repo.get_all_assignments()
        return [self._to_response(a) for a in assignments]

    def get_assignments_by_creator_id(self, creator_id: int) -> list[AssignmentResponseDTO]:
        assignments = self._repo.get_all_assignments_by_creator_id(creator_id)
        return [self._to_response(a) for a in assignments]

    def get_assignment_by_id(self, assignment_id: int) -> AssignmentResponseDTO:
        assignment = self._repo.get_assignment_by_id(assignment_id)
        return self._to_response(assignment)

    async def edit_assignment(self, assignment_id: int, dto: EditAssignmentDTO) -> AssignmentResponseDTO:
        assignment = self._repo.get_assignment_by_id(assignment_id)
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

        fields = dto.model_dump(exclude_none=True)
        if not fields:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided to update")

        updated = self._repo.update_assignment(assignment_id, fields)

        await OutboxService().process_pending_events()
        return self._to_response(updated)

    @staticmethod
    def _to_response(assignment: Assignment) -> AssignmentResponseDTO:
        return AssignmentResponseDTO(
            id=assignment.id,
            creator_id=assignment.creator_id,
            description=assignment.description,
            name=assignment.name,
            status=assignment.status,
            start_time=assignment.start_time,
            stop_grade_time=assignment.stop_grade_time,
            stop_submit_time=assignment.stop_submit_time,
            submission_count=assignment.submission_count,
            type=assignment.type,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )

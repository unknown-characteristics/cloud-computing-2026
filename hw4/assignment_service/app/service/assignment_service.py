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
from app.repository.assignment_repository import AssignmentRepository
from app.repository.outbox_repository import OutboxRepository
from app.helpers.datetime_helpers import is_past
from app.service.outbox_service import OutboxService
from app.core.datastore_client import get_datastore_client
from app.core.task_client import schedule_task

class AssignmentService:
    def __init__(self):
        self._repo = AssignmentRepository()
        self._outbox_repo = OutboxRepository()
        self._client = get_datastore_client()

    async def create_assignment(self, dto: CreateAssignmentDTO) -> AssignmentResponseDTO:
        assignment = Assignment(**dto.model_dump())
        assignment.status = "active"
        with self._client.transaction():
            created = self._repo.create(assignment)

            # Write to outbox for reliable Pub/Sub delivery
            self._outbox_repo.create(OutboxEvent(
                data=json.dumps({"assignment_id": created.id, "name": created.name, "creator_id": created.creator_id}),
                event_id=str(uuid.uuid4()),
                event_type="assignment.created",
                pending=True,
            ))

            # --- Schedule Cloud Tasks for the two deadlines ---
    
            # Task 1: fires at stop_submit_time
            schedule_task(
                url_path=f"/assignments/check-deadline/{created.id}",
                payload={"deadline_type": "stop_submit"},
                schedule_time=created.stop_submit_time,
            )
        
            # Task 2: fires at stop_grade_time
            schedule_task(
                url_path=f"/assignments/check-deadline/{created.id}",
                payload={"deadline_type": "stop_grade"},
                schedule_time=created.stop_grade_time,
            )
        
        await OutboxService().process_pending_events()

        return self._to_response(created)
    
    async def delete_assignment(self, assignment_id: int) -> None:
        with self._client.transaction():
            assignment = self._repo.get_by_id(assignment_id)
            if not assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
            deleted = self._repo.delete(assignment_id)
            if not deleted:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete assignment")

            self._outbox_repo.create(OutboxEvent(
                data=json.dumps({"assignment_id": assignment_id, "name": assignment.name, "creator_id": assignment.creator_id}),
                event_id=str(uuid.uuid4()),
                event_type="assignment.deleted",
                pending=True,
            ))

        await OutboxService().process_pending_events()

    def get_assignments(self) -> list[AssignmentResponseDTO]:
        assignments = self._repo.get_all()
        return [self._to_response(a) for a in assignments]

    def get_assignments_by_creator_id(self, creator_id: int) -> list[AssignmentResponseDTO]:
        assignments = self._repo.get_all_by_creator_id(creator_id)
        return [self._to_response(a) for a in assignments]

    def get_assignment_by_id(self, assignment_id: int) -> AssignmentResponseDTO:
        assignment = self._repo.get_by_id(assignment_id)
        return self._to_response(assignment)

    async def edit_assignment(self, assignment_id: int, dto: EditAssignmentDTO) -> AssignmentResponseDTO:
        with self._client.transaction():
            assignment = self._repo.get_by_id(assignment_id)
            if not assignment:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

            fields = dto.model_dump(exclude_none=True)
            if not fields:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided to update")

            updated = self._repo.update(assignment_id, fields)

            self._outbox_repo.create(OutboxEvent(
                data=json.dumps({"assignment_id": assignment_id, "status": updated.status}),
                event_id=str(uuid.uuid4()),
                event_type="assignment.updated",
                pending=True,
            ))

        await OutboxService().process_pending_events()
        return self._to_response(updated)

    # def get_leaderboard(self) -> LeaderboardResponseDTO:
    #     return self.compute_leaderboard()

    # def compute_leaderboard(self) -> LeaderboardResponseDTO:
    #     assignments = self._repo.get_all_ordered_by_submissions()
    #     entries = [
    #         LeaderboardEntryDTO(
    #             assignment_id=a.id,
    #             name=a.name,
    #             submission_count=a.submission_count,
    #             rank=idx + 1,
    #         )
    #         for idx, a in enumerate(assignments)
    #     ]
    #     return LeaderboardResponseDTO(entries=entries, total=len(entries))

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

import json
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.dtos.assignment_dto import (
    CreateAssignmentDTO,
    EditAssignmentDTO,
    AssignmentResponseDTO,
    LeaderboardEntryDTO,
    LeaderboardResponseDTO,
)
from app.models.assignment import Assignment
from app.models.outbox import OutboxEvent
from app.repository.assignment_repository import AssignmentRepository
from app.repository.outbox_repository import OutboxRepository
from app.helpers.datetime_helpers import is_past


class AssignmentService:
    def __init__(self):
        self._repo = AssignmentRepository()
        self._outbox_repo = OutboxRepository()

    async def create_assignment(self, dto: CreateAssignmentDTO) -> AssignmentResponseDTO:
        assignment = Assignment(**dto.model_dump())
        created = await self._repo.create(assignment)

        # Write to outbox for reliable Pub/Sub delivery
        await self._outbox_repo.create(OutboxEvent(
            data=json.dumps({"assignment_id": created.id, "name": created.name}),
            event_id=str(uuid.uuid4()),
            event_type="assignment.created",
            pending=True,
        ))

        return self._to_response(created)

    async def delete_assignment(self, assignment_id: str) -> None:
        assignment = await self._repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

        deleted = await self._repo.delete(assignment_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete assignment")

        await self._outbox_repo.create(OutboxEvent(
            data=json.dumps({"assignment_id": assignment_id}),
            event_id=str(uuid.uuid4()),
            event_type="assignment.deleted",
            pending=True,
        ))

    async def get_assignments(self) -> list[AssignmentResponseDTO]:
        assignments = await self._repo.get_all()
        return [self._to_response(a) for a in assignments]

    async def edit_assignment(self, assignment_id: str, dto: EditAssignmentDTO) -> AssignmentResponseDTO:
        assignment = await self._repo.get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

        fields = dto.model_dump(exclude_none=True)
        if not fields:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided to update")

        updated = await self._repo.update(assignment_id, fields)

        await self._outbox_repo.create(OutboxEvent(
            data=json.dumps({"assignment_id": assignment_id, "updated_fields": list(fields.keys())}),
            event_id=str(uuid.uuid4()),
            event_type="assignment.updated",
            pending=True,
        ))

        return self._to_response(updated)

    async def deadline_reached(self) -> list[AssignmentResponseDTO]:
        """Returns all assignments whose submission deadline has passed."""
        assignments = await self._repo.get_past_deadline()
        return [self._to_response(a) for a in assignments]

    async def get_leaderboard(self) -> LeaderboardResponseDTO:
        return await self.compute_leaderboard()

    async def compute_leaderboard(self) -> LeaderboardResponseDTO:
        assignments = await self._repo.get_all_ordered_by_submissions()
        entries = [
            LeaderboardEntryDTO(
                assignment_id=a.id,
                name=a.name,
                submission_count=a.submission_count,
                rank=idx + 1,
            )
            for idx, a in enumerate(assignments)
        ]
        return LeaderboardResponseDTO(entries=entries, total=len(entries))

    @staticmethod
    def _to_response(assignment: Assignment) -> AssignmentResponseDTO:
        return AssignmentResponseDTO(
            id=assignment.id,
            creator_id=assignment.creator_id,
            description=assignment.description,
            name=assignment.name,
            start_time=assignment.start_time,
            stop_grade_time=assignment.stop_grade_time,
            stop_submit_time=assignment.stop_submit_time,
            submission_count=assignment.submission_count,
            type=assignment.type,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )

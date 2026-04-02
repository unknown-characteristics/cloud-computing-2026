import json, uuid
from fastapi import HTTPException
from app.dtos.submission_dto import CreateSubmissionDTO, UpdateSubmissionDTO, SubmissionResponseDTO
from app.models.submission import Submission
from app.models.outbox import OutboxEvent
from app.repository.submission_repo import SubmissionRepository
from app.repository.outbox_repo import OutboxRepository
from app.helpers.datetime_helpers import utcnow


class SubmissionService:
    def __init__(self):
        self._repo = SubmissionRepository()
        self._outbox = OutboxRepository()

    async def create(self, dto: CreateSubmissionDTO) -> SubmissionResponseDTO:
        sub = await self._repo.create(Submission(**dto.model_dump()))
        await self._log_event(sub.id, sub.assignment_id, "submission.created")
        return SubmissionResponseDTO(**sub.model_dump())

    async def get_all_by_assignment(self, assignment_id: str) -> list[SubmissionResponseDTO]:
        subs = await self._repo.get_all_active_by_assignment(assignment_id)
        return [SubmissionResponseDTO(**s.model_dump()) for s in subs]

    async def update(self, sub_id: str, dto: UpdateSubmissionDTO) -> SubmissionResponseDTO:
        if not await self._repo.get_by_id(sub_id):
            raise HTTPException(status_code=404, detail="Submission not found")

        fields = dto.model_dump(exclude_none=True)
        updated = await self._repo.update(sub_id, fields)
        await self._log_event(sub_id, updated.assignment_id, "submission.updated", fields)
        return SubmissionResponseDTO(**updated.model_dump())

    async def delete(self, sub_id: str) -> None:
        sub = await self._repo.get_by_id(sub_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")

        await self._repo.update(sub_id, {"status": "deleted", "deleted_at": utcnow()})
        await self._log_event(sub_id, sub.assignment_id, "submission.deleted")

    async def _log_event(self, sub_id: str, assign_id: str, ev_type: str, extra: dict = None):
        data = {"submission_id": sub_id, "assignment_id": assign_id}
        if extra: data.update(extra)
        await self._outbox.create(OutboxEvent(
            data=json.dumps(data), event_id=str(uuid.uuid4()), event_type=ev_type, pending=True
        ))
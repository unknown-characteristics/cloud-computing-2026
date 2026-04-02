import json, uuid
from fastapi import HTTPException
from app.dtos.rating_dto import CreateRatingDTO, UpdateRatingDTO, RatingResponseDTO
from app.models.rating import Rating
from app.models.outbox import OutboxEvent
from app.repository.rating_repo import RatingRepository
from app.repository.outbox_repo import OutboxRepository
from app.repository.submission_repo import SubmissionRepository
from app.helpers.datetime_helpers import utcnow


class RatingService:
    def __init__(self):
        self._repo = RatingRepository()
        self._sub_repo = SubmissionRepository()
        self._outbox = OutboxRepository()

    async def create(self, dto: CreateRatingDTO) -> RatingResponseDTO:
        # Validare: submisia trebuie să existe și să fie activă
        if not await self._sub_repo.get_by_id(dto.submission_id):
            raise HTTPException(status_code=404, detail="Submission not found")

        rating = await self._repo.create(Rating(**dto.model_dump()))
        await self._log_event(rating.id, rating.submission_id, "rating.created")
        return RatingResponseDTO(**rating.model_dump())

    async def get_by_submission(self, sub_id: str) -> list[RatingResponseDTO]:
        ratings = await self._repo.get_active_by_submission(sub_id)
        return [RatingResponseDTO(**r.model_dump()) for r in ratings]

    async def update(self, rating_id: str, dto: UpdateRatingDTO) -> RatingResponseDTO:
        if not await self._repo.get_by_id(rating_id):
            raise HTTPException(status_code=404, detail="Rating not found")

        fields = dto.model_dump(exclude_none=True)
        updated = await self._repo.update(rating_id, fields)
        await self._log_event(rating_id, updated.submission_id, "rating.updated", fields)
        return RatingResponseDTO(**updated.model_dump())

    async def delete(self, rating_id: str) -> None:
        rating = await self._repo.get_by_id(rating_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")

        await self._repo.update(rating_id, {"status": "deleted", "deleted_at": utcnow()})
        await self._log_event(rating_id, rating.submission_id, "rating.deleted")

    async def _log_event(self, rating_id: str, sub_id: str, ev_type: str, extra: dict = None):
        data = {"rating_id": rating_id, "submission_id": sub_id}
        if extra: data.update(extra)
        await self._outbox.create(OutboxEvent(
            data=json.dumps(data), event_id=str(uuid.uuid4()), event_type=ev_type, pending=True
        ))
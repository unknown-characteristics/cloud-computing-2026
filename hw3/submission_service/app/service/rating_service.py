import json, uuid
from fastapi import HTTPException
from app.dtos.rating_dto import CreateRatingDTO, UpdateRatingDTO, RatingResponseDTO
from app.models.rating import Rating
from app.models.outbox import OutboxEvent
from app.repository.rating_repo import RatingRepository
from app.repository.outbox_repo import OutboxRepository
from app.repository.submission_repo import SubmissionRepository
from app.helpers.datetime_helpers import utcnow
from app.service.outbox_service import OutboxService

class RatingService:
    def __init__(self):
        self._repo = RatingRepository()
        self._sub_repo = SubmissionRepository()
        self._outbox = OutboxRepository()

    async def create(self, dto: CreateRatingDTO, user_id: int) -> RatingResponseDTO:
        if not self._sub_repo.get_by_id(dto.submission_id):
            raise HTTPException(status_code=404, detail="Submission not found")

        rating_data = dto.model_dump()
        rating_data["user_id"] = user_id

        rating = self._repo.create(Rating(**rating_data))
        self._log_event(rating.id, rating.submission_id, "rating.created")
        await OutboxService().process_pending_events()
        return RatingResponseDTO(**rating.model_dump())

    def get_by_submission(self, sub_id: int) -> list[RatingResponseDTO]:
        ratings = self._repo.get_active_by_submission(sub_id)
        return [RatingResponseDTO(**r.model_dump()) for r in ratings]

    async def update(self, rating_id: int, dto: UpdateRatingDTO, user_id: int) -> RatingResponseDTO:
        rating = self._repo.get_by_id(rating_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        if rating.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this rating")

        fields = dto.model_dump(exclude_none=True)
        updated = self._repo.update(rating_id, fields)
        self._log_event(rating_id, updated.submission_id, "rating.updated", fields)
        await OutboxService().process_pending_events()
        return RatingResponseDTO(**updated.model_dump())

    async def delete(self, rating_id: int, user_id: int) -> None:
        rating = self._repo.get_by_id(rating_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        if rating.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this rating")

        self._repo.update(rating_id, {"status": "deleted", "deleted_at": utcnow()})
        self._log_event(rating_id, rating.submission_id, "rating.deleted")
        await OutboxService().process_pending_events()

    def _log_event(self, rating_id: int, sub_id: int, ev_type: str, extra: dict = None):
        data = {"rating_id": rating_id, "submission_id": sub_id}
        if extra: data.update(extra)
        self._outbox.create(OutboxEvent(
            data=json.dumps(data), event_id=str(uuid.uuid4()), event_type=ev_type, pending=True
        ))

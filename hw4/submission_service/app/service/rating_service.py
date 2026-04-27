import json, uuid
from fastapi import HTTPException
from app.dtos.rating_dto import CreateRatingDTO, UpdateRatingDTO, RatingResponseDTO
from app.models.rating import Rating
from app.models.outbox import OutboxEvent
from app.repository.rating_repo import RatingRepository
from app.repository.submission_repo import SubmissionRepository
from app.helpers.datetime_helpers import utcnow
from app.service.outbox_service import OutboxService

class RatingService:
    def __init__(self):
        self._repo = RatingRepository()
        self._sub_repo = SubmissionRepository()

    async def create(self, dto: CreateRatingDTO, user_id: int) -> RatingResponseDTO:
        if not self._sub_repo.get_submission_by_id(dto.submission_id):
            raise HTTPException(status_code=404, detail="Submission not found")

        rating_data = dto.model_dump()
        rating_data["user_id"] = user_id

        try:
            rating = self._repo.create_with_outbox(Rating(**rating_data))
        except ValueError as e:
            if "Rating already exists" in e.args[0]:
                raise HTTPException(status_code=400, detail=e.args[0])

        await OutboxService().process_pending_events()
        return RatingResponseDTO(**rating.model_dump())

    def get_by_submission(self, sub_id: str) -> list[RatingResponseDTO]:
        ratings = self._repo.get_all_active_ratings_by_submission_id(sub_id)
        return [RatingResponseDTO(**r.model_dump()) for r in ratings]

    async def update(self, rating_id: str, dto: UpdateRatingDTO, user_id: int) -> RatingResponseDTO:
        rating = self._repo.get_rating_by_id(rating_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        if rating.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this rating")

        fields = dto.model_dump(exclude_none=True)
        updated = self._repo.update_rating(rating_id, fields)
        await OutboxService().process_pending_events()
        return RatingResponseDTO(**updated.model_dump())

    async def delete(self, rating_id: str, user_id: int) -> None:
        rating = self._repo.get_rating_by_id(rating_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        if rating.user_id != user_id and user_id != -1:
            raise HTTPException(status_code=403, detail="Not authorized to delete this rating")

        self._repo.update_rating(rating_id, {"status": "deleted", "deleted_at": utcnow()})
        await OutboxService().process_pending_events()

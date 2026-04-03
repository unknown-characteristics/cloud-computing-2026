from typing import Optional, List
from google.cloud import datastore
from app.models.rating import Rating
from app.helpers.datetime_helpers import utcnow


class RatingRepository:
    def __init__(self):
        self._client = datastore.Client()
        self._kind = "rating"

    # --- Helper to build a deterministic key for uniqueness ---
    def _build_key(self, submission_id: str, user_id: str):
        # Example: one rating per user per submission
        return self._client.key(self._kind, f"{submission_id}_{user_id}")

    # --- Create a rating ---
    def create(self, rating: Rating) -> Rating:
        key = self._build_key(rating.submission_id, str(rating.user_id))

        # Prevent overwrite
        if self._client.get(key):
            raise ValueError(
                f"Rating already exists for submission_id={rating.submission_id} "
                f"and user_id={rating.user_id}"
            )

        rating.created_at = rating.updated_at = utcnow()

        entity = datastore.Entity(key=key)
        entity.update(rating.model_dump(exclude={"id"}))

        self._client.put(entity)
        rating.id = key.name  # deterministic string key
        return rating

    # --- Get rating by ID ---
    def get_by_id(self, rating_id: str) -> Optional[Rating]:
        key = self._client.key(self._kind, rating_id)
        entity = self._client.get(key)
        if not entity or entity.get("status") == "deleted":
            return None
        return self._build_rating(entity)

    # --- Get all active ratings for a submission ---
    def get_active_by_submission(self, submission_id: str) -> List[Rating]:
        query = self._client.query(kind=self._kind)
        query.add_filter("submission_id", "=", submission_id)
        query.add_filter("status", "=", "active")
        entities = list(query.fetch())
        return [self._build_rating(e) for e in entities]

    # --- Update fields for a rating ---
    def update(self, rating_id: str, fields: dict) -> Rating:
        key = self._client.key(self._kind, rating_id)
        entity = self._client.get(key)
        if not entity:
            raise ValueError(f"Rating with id {rating_id} not found")

        fields["updated_at"] = utcnow()
        entity.update(fields)
        self._client.put(entity)
        return self._build_rating(entity)

    # --- Helper to construct Rating safely ---
    def _build_rating(self, entity) -> Rating:
        data = {k: v for k, v in entity.items() if k != "id"}
        return Rating(id=entity.key.name, **data)

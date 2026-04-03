from typing import Optional
from google.cloud import datastore
from app.models.rating import Rating
from app.helpers.datetime_helpers import utcnow

class RatingRepository:
    def __init__(self):
        self._client = datastore.Client()
        self._kind = "rating"

    def create(self, rating: Rating) -> Rating:
        rating.created_at = rating.updated_at = utcnow()
        key = self._client.key(self._kind)
        key = self._client.allocate_ids(key, 1)[0]
        entity = datastore.Entity(key=key)
        entity.update(rating.model_dump(exclude={"id"}))
        self._client.put(entity)
        rating.id = str(entity.key.id)
        return rating

    def get_by_id(self, rating_id: str) -> Optional[Rating]:
        key = self._client.key(self._kind, int(rating_id))
        entity = self._client.get(key)
        if not entity or entity.get("status") == "deleted":
            return None
        return Rating(id=str(entity.key.id), **entity)

    def get_active_by_submission(self, submission_id: str) -> list[Rating]:
        query = self._client.query(kind=self._kind)
        query.add_filter("submission_id", "=", submission_id)
        query.add_filter("status", "=", "active")
        entities = list(query.fetch())
        return [Rating(id=str(e.key.id), **e) for e in entities]

    def update(self, rating_id: str, fields: dict) -> Rating:
        fields["updated_at"] = utcnow()
        key = self._client.key(self._kind, int(rating_id))
        entity = self._client.get(key)
        if not entity:
            raise ValueError(f"Rating with id {rating_id} not found")
        entity.update(fields)
        self._client.put(entity)
        return Rating(id=str(entity.key.id), **entity)

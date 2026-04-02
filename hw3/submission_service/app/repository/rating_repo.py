from typing import Optional
from google.cloud import firestore
from app.core.firestore_client import get_firestore_client
from app.models.rating import Rating
from app.helpers.datetime_helpers import utcnow

class RatingRepository:
    def __init__(self):
        self._db = get_firestore_client()
        self._collection = self._db.collection("ratings")

    async def create(self, rating: Rating) -> Rating:
        rating.created_at = rating.updated_at = utcnow()
        doc_ref = self._collection.document()
        await doc_ref.set(rating.model_dump(exclude={"id"}))
        rating.id = doc_ref.id
        return rating

    async def get_by_id(self, rating_id: str) -> Optional[Rating]:
        doc = await self._collection.document(rating_id).get()
        if not doc.exists or doc.to_dict().get("status") == "deleted":
            return None
        return Rating(id=doc.id, **doc.to_dict())

    async def get_active_by_submission(self, submission_id: str) -> list[Rating]:
        docs = self._collection.where("submission_id", "==", submission_id).where("status", "==", "active").stream()
        return [Rating(id=doc.id, **doc.to_dict()) async for doc in docs]

    async def update(self, rating_id: str, fields: dict) -> Rating:
        fields["updated_at"] = utcnow()
        doc_ref = self._collection.document(rating_id)
        await doc_ref.update(fields)
        updated = await doc_ref.get()
        return Rating(id=updated.id, **updated.to_dict())
from typing import Optional
from google.cloud import firestore
from app.core.firestore_client import get_firestore_client
from app.models.submission import Submission
from app.helpers.datetime_helpers import utcnow

class SubmissionRepository:
    def __init__(self):
        self._db = get_firestore_client()
        self._collection = self._db.collection("submissions")

    async def create(self, sub: Submission) -> Submission:
        sub.created_at = sub.updated_at = utcnow()
        doc_ref = self._collection.document()
        await doc_ref.set(sub.model_dump(exclude={"id"}))
        sub.id = doc_ref.id
        return sub

    async def get_by_id(self, sub_id: str) -> Optional[Submission]:
        doc = await self._collection.document(sub_id).get()
        if not doc.exists or doc.to_dict().get("status") == "deleted":
            return None
        return Submission(id=doc.id, **doc.to_dict())

    async def get_all_active_by_assignment(self, assignment_id: str) -> list[Submission]:
        docs = self._collection.where("assignment_id", "==", assignment_id).where("status", "==", "active").stream()
        return [Submission(id=doc.id, **doc.to_dict()) async for doc in docs]

    async def update(self, sub_id: str, fields: dict) -> Submission:
        fields["updated_at"] = utcnow()
        doc_ref = self._collection.document(sub_id)
        await doc_ref.update(fields)
        updated = await doc_ref.get()
        return Submission(id=updated.id, **updated.to_dict())
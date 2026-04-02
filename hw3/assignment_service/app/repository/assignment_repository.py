from datetime import datetime, timezone
from typing import Optional

from google.cloud import firestore

from app.core.firestore_client import get_firestore_client
from app.models.assignment import Assignment

COLLECTION = "assignments"


class AssignmentRepository:
    def __init__(self):
        self._db: firestore.AsyncClient = get_firestore_client()

    @property
    def _collection(self):
        return self._db.collection(COLLECTION)

    async def create(self, assignment: Assignment) -> Assignment:
        now = datetime.now(timezone.utc)
        assignment.created_at = now
        assignment.updated_at = now

        data = assignment.model_dump(exclude={"id"})
        doc_ref = self._collection.document()
        await doc_ref.set(data)
        assignment.id = doc_ref.id
        return assignment

    async def get_by_id(self, assignment_id: str) -> Optional[Assignment]:
        doc = await self._collection.document(assignment_id).get()
        if not doc.exists:
            return None
        return Assignment(id=doc.id, **doc.to_dict())

    async def get_all(self) -> list[Assignment]:
        docs = self._collection.stream()
        assignments = []
        async for doc in docs:
            assignments.append(Assignment(id=doc.id, **doc.to_dict()))
        return assignments

    async def update(self, assignment_id: str, fields: dict) -> Optional[Assignment]:
        doc_ref = self._collection.document(assignment_id)
        doc = await doc_ref.get()
        if not doc.exists:
            return None
        fields["updated_at"] = datetime.now(timezone.utc)
        await doc_ref.update(fields)
        updated = await doc_ref.get()
        return Assignment(id=updated.id, **updated.to_dict())

    async def delete(self, assignment_id: str) -> bool:
        doc_ref = self._collection.document(assignment_id)
        doc = await doc_ref.get()
        if not doc.exists:
            return False
        await doc_ref.delete()
        return True

    async def get_past_deadline(self) -> list[Assignment]:
        now = datetime.now(timezone.utc)
        docs = (
            self._collection
            .where("stop_submit_time", "<=", now)
            .stream()
        )
        assignments = []
        async for doc in docs:
            assignments.append(Assignment(id=doc.id, **doc.to_dict()))
        return assignments

    async def get_all_ordered_by_submissions(self) -> list[Assignment]:
        docs = (
            self._collection
            .order_by("submission_count", direction=firestore.Query.DESCENDING)
            .stream()
        )
        assignments = []
        async for doc in docs:
            assignments.append(Assignment(id=doc.id, **doc.to_dict()))
        return assignments

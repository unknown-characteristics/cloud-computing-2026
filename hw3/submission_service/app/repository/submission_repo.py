from typing import Optional
from google.cloud import datastore
from app.models.submission import Submission
from app.helpers.datetime_helpers import utcnow

class SubmissionRepository:
    def __init__(self):
        self._client = datastore.Client()
        self._kind = "submission"

    def create(self, sub: Submission) -> Submission:
        sub.created_at = sub.updated_at = utcnow()
        key = self._client.key(self._kind)
        entity = datastore.Entity(key=key)
        entity.update(sub.model_dump(exclude={"id"}))
        self._client.put(entity)
        sub.id = str(entity.key.id)
        return sub

    def get_by_id(self, sub_id: str) -> Optional[Submission]:
        key = self._client.key(self._kind, int(sub_id))
        entity = self._client.get(key)
        if not entity or entity.get("status") == "deleted":
            return None
        return Submission(id=str(entity.key.id), **entity)

    def get_all_active_by_assignment(self, assignment_id: str) -> list[Submission]:
        query = self._client.query(kind=self._kind)
        query.add_filter("assignment_id", "=", assignment_id)
        query.add_filter("status", "=", "active")
        entities = list(query.fetch())
        return [Submission(id=str(e.key.id), **e) for e in entities]

    def update(self, sub_id: str, fields: dict) -> Submission:
        fields["updated_at"] = utcnow()
        key = self._client.key(self._kind, int(sub_id))
        entity = self._client.get(key)
        if not entity:
            raise ValueError(f"Submission with id {sub_id} not found")
        entity.update(fields)
        self._client.put(entity)
        return Submission(id=str(entity.key.id), **entity)

from datetime import datetime, timezone
from typing import Optional

from google.cloud import datastore

from app.core.datastore_client import get_datastore_client
from app.models.assignment import Assignment

KIND = "assignment"

class AssignmentRepository:
    def __init__(self):
        self._db: datastore.Client = get_datastore_client()

    def _key(self, assignment_id: Optional[str] = None):
        if assignment_id:
            return self._db.key(KIND, assignment_id)
        return self._db.key(KIND)

    def create(self, assignment: Assignment) -> Assignment:
        now = datetime.now(timezone.utc)
        assignment.created_at = now
        assignment.updated_at = now

        key = self._key()
        entity = datastore.Entity(key=key)

        data = assignment.model_dump(exclude={"id"})
        entity.update(data)

        self._db.put(entity)

        assignment.id = entity.key.id or entity.key.name
        return assignment

    def get_by_id(self, assignment_id: str) -> Optional[Assignment]:
        key = self._key(assignment_id)
        entity = self._db.get(key)
        if not entity:
            return None

        return Assignment(id=entity.key.id or entity.key.name, **dict(entity))

    def get_all(self) -> list[Assignment]:
        query = self._db.query(kind=KIND)
        results = query.fetch()

        assignments = []
        for entity in results:
            assignments.append(
                Assignment(id=entity.key.id or entity.key.name, **dict(entity))
            )
        return assignments

    def update(self, assignment_id: str, fields: dict) -> Optional[Assignment]:
        key = self._key(assignment_id)
        entity = self._db.get(key)
        if not entity:
            return None

        fields["updated_at"] = datetime.now(timezone.utc)
        entity.update(fields)

        self._db.put(entity)

        return Assignment(id=entity.key.id or entity.key.name, **dict(entity))

    def delete(self, assignment_id: str) -> bool:
        key = self._key(assignment_id)
        entity = self._db.get(key)
        if not entity:
            return False

        self._db.delete(key)
        return True

    def get_past_deadline(self) -> list[Assignment]:
        now = datetime.now(timezone.utc)

        query = self._db.query(kind=KIND)
        query.add_filter("stop_submit_time", "<=", now)

        results = query.fetch()

        assignments = []
        for entity in results:
            assignments.append(
                Assignment(id=entity.key.id or entity.key.name, **dict(entity))
            )
        return assignments

    def get_all_ordered_by_submissions(self) -> list[Assignment]:
        query = self._db.query(kind=KIND)
        query.order = ["-submission_count"]  # descending

        results = query.fetch()

        assignments = []
        for entity in results:
            assignments.append(
                Assignment(id=entity.key.id or entity.key.name, **dict(entity))
            )
        return assignments

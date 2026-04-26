from typing import Optional
from google.cloud import datastore
from app.models.submission import Submission
from app.helpers.datetime_helpers import utcnow


class SubmissionRepository:
    def __init__(self):
        self._client = datastore.Client()
        self._kind = "submission"

    def _build_key(self, user_id: int, assignment_id: int):
        # Deterministic composite key → guarantees uniqueness
        return self._client.key(
            self._kind,
            f"{user_id}_{assignment_id}"
        )

    def create(self, sub: Submission) -> Submission:
        key = self._build_key(sub.user_id, sub.assignment_id)

        # Prevent overwrite (optional but recommended)
        old = self._client.get(key)
        if old is not None and old["status"] != "deleted":
            raise ValueError(
                f"Submission already exists for user_id={sub.user_id} "
                f"and assignment_id={sub.assignment_id}"
            )

        sub.created_at = sub.updated_at = utcnow()

        entity = datastore.Entity(key=key)
        entity.update(sub.model_dump(exclude={"id"}))

        self._client.put(entity)

        # Key is string-based now
        sub.id = key.name
        return sub

    def get_by_id(self, sub_id: str) -> Optional[Submission]:
        key = self._client.key(self._kind, sub_id)
        entity = self._client.get(key)

        if not entity or entity.get("status") == "deleted":
            return None

        return Submission(id=entity.key.name, **entity)

    def get_all_active_by_assignment(self, assignment_id: int) -> list[Submission]:
        query = self._client.query(kind=self._kind)
        query.add_filter("assignment_id", "=", assignment_id)
        query.add_filter("status", "=", "active")

        entities = list(query.fetch())
        return [Submission(id=e.key.name, **e) for e in entities]
        # out =  [Submission(id=e.key.name, **{k: v for k, v in e.items() if k != "id"}) for e in entities]
        # print(entities[0].key)
        # print(out)
        # print(out[0].model_dump())
        # print(entities[0].key.name)
        # return out

    def get_all_active_by_user(self, user_id: int) -> list[Submission]:
        query = self._client.query(kind=self._kind)
        query.add_filter("user_id", "=", user_id)
        query.add_filter("status", "=", "active")

        entities = list(query.fetch())
        return [Submission(id=e.key.name, **e) for e in entities]

    def update(self, sub_id: str, fields: dict) -> Submission:
        fields["updated_at"] = utcnow()

        key = self._client.key(self._kind, sub_id)
        entity = self._client.get(key)

        if not entity:
            raise ValueError(f"Submission with id {sub_id} not found")

        entity.update(fields)
        self._client.put(entity)

        return Submission(id=entity.key.name, **entity)

    def get_all(self):
        query = self.client.query(kind=self.kind)
        results = list(query.fetch())

        submissions = []
        for r in results:
            sub = Submission(**r)
            # Datastore pune ID-ul in key, trebuie sa il scoatem
            sub.id = r.key.name
            submissions.append(sub)

        return submissions

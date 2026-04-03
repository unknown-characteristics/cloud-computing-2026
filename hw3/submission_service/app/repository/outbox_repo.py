from google.cloud import datastore

from app.core.datastore_client import get_datastore_client
from app.models.outbox import OutboxEvent

KIND = "outbox"

class OutboxRepository:
    def __init__(self):
        self._db: datastore.Client = get_datastore_client()

    def _key(self, event_id: str | None = None):
        if event_id:
            return self._db.key(KIND, event_id)
        return self._db.key(KIND)

    def create(self, event: OutboxEvent) -> OutboxEvent:
        key = self._key()
        key = self._client.allocate_ids(key, 1)[0]
        entity = datastore.Entity(key=key)

        data = event.model_dump(exclude={"id"})
        entity.update(data)

        self._db.put(entity)

        event.id = entity.key.id or entity.key.name
        return event

    def get_pending(self) -> list[OutboxEvent]:
        query = self._db.query(kind=KIND)
        query.add_filter("pending", "=", True)

        results = query.fetch()

        events = []
        for entity in results:
            events.append(
                OutboxEvent(id=entity.key.id or entity.key.name, **dict(entity))
            )
        return events

    def mark_as_published(self, event_id: str) -> None:
        key = self._key(event_id)
        entity = self._db.get(key)

        if not entity:
            return

        entity["pending"] = False
        self._db.put(entity)

    def get_all(self) -> list[OutboxEvent]:
        query = self._db.query(kind=KIND)
        results = query.fetch()

        events = []
        for entity in results:
            events.append(
                OutboxEvent(id=entity.key.id or entity.key.name, **dict(entity))
            )
        return events

from google.cloud import datastore

from app.core.datastore_client import get_datastore_client
from app.models.other_event import OtherEvent

KIND = "other-events"

class OtherEventRepository:
    def __init__(self):
        self._db: datastore.Client = get_datastore_client()

    def _key(self, event_id: str):
        return self._db.key(KIND, event_id)

    def exists(self, event_id: str) -> bool:
        key = self._key(event_id)
        entity = self._db.get(key)
        return entity is not None

    def create(self, event_id: str) -> OtherEvent:
        key = self._key(event_id)

        # Prevent overwrite if already exists
        if self._db.get(key):
            raise ValueError(f"OtherEvent with event_id '{event_id}' already exists")

        event = OtherEvent(event_id=event_id)
        entity = datastore.Entity(key=key)

        entity.update(event.model_dump(exclude={"id"}))
        self._db.put(entity)

        event.id = event_id  # key name = event_id
        return event

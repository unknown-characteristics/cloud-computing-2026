from google.cloud import firestore

from app.core.firestore_client import get_firestore_client
from app.models.other_event import OtherEvent

COLLECTION = "other_events"


class OtherEventRepository:
    def __init__(self):
        self._db: firestore.AsyncClient = get_firestore_client()

    @property
    def _collection(self):
        return self._db.collection(COLLECTION)

    async def exists(self, event_id: str) -> bool:
        docs = self._collection.where("event_id", "==", event_id).limit(1).stream()
        async for _ in docs:
            return True
        return False

    async def create(self, event_id: str) -> OtherEvent:
        event = OtherEvent(event_id=event_id)
        doc_ref = self._collection.document()
        await doc_ref.set(event.model_dump(exclude={"id"}))
        event.id = doc_ref.id
        return event

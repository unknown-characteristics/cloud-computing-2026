from google.cloud import firestore

from app.core.firestore_client import get_firestore_client
from app.models.outbox import OutboxEvent

COLLECTION = "outbox"


class OutboxRepository:
    def __init__(self):
        self._db: firestore.AsyncClient = get_firestore_client()

    @property
    def _collection(self):
        return self._db.collection(COLLECTION)

    async def create(self, event: OutboxEvent) -> OutboxEvent:
        data = event.model_dump(exclude={"id"})
        doc_ref = self._collection.document()
        await doc_ref.set(data)
        event.id = doc_ref.id
        return event

    async def get_pending(self) -> list[OutboxEvent]:
        docs = self._collection.where("pending", "==", True).stream()
        events = []
        async for doc in docs:
            events.append(OutboxEvent(id=doc.id, **doc.to_dict()))
        return events

    async def mark_as_published(self, event_id: str) -> None:
        await self._collection.document(event_id).update({"pending": False})

    async def get_all(self) -> list[OutboxEvent]:
        docs = self._collection.stream()
        events = []
        async for doc in docs:
            events.append(OutboxEvent(id=doc.id, **doc.to_dict()))
        return events

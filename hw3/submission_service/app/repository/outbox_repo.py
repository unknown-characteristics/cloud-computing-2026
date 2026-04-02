from app.core.firestore_client import get_firestore_client
from app.models.outbox import OutboxEvent

class OutboxRepository:
    def __init__(self):
        self._db = get_firestore_client()
        self._collection = self._db.collection("outbox")

    async def create(self, event: OutboxEvent) -> OutboxEvent:
        doc_ref = self._collection.document()
        await doc_ref.set(event.model_dump(exclude={"id"}))
        event.id = doc_ref.id
        return event

    async def get_pending(self) -> list[OutboxEvent]:
        docs = self._collection.where("pending", "==", True).stream()
        return [OutboxEvent(id=doc.id, **doc.to_dict()) async for doc in docs]

    async def mark_as_published(self, event_id: str) -> None:
        await self._collection.document(event_id).update({"pending": False})
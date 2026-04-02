from typing import Optional
from pydantic import BaseModel


class OutboxEvent(BaseModel):
    """
    Mirrors the Firestore 'outbox' kind schema.
    Used for the reliable outbox pattern with Pub/Sub.
    """
    id: Optional[str] = None   # Firestore document ID
    data: str
    event_id: str
    event_type: str
    pending: bool = True

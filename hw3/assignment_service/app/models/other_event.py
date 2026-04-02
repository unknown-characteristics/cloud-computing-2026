from typing import Optional
from pydantic import BaseModel


class OtherEvent(BaseModel):
    """
    Mirrors the Firestore 'other_events' kind schema.
    Tracks already-handled external events to ensure idempotency.
    """
    id: Optional[str] = None   # Firestore document ID
    event_id: str

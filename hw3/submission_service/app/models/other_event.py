from typing import Optional
from pydantic import BaseModel


class OtherEvent(BaseModel):
    """
    Mirrors the Datastore 'other-events' kind schema.
    Tracks already-handled external events to ensure idempotency.
    """
    id: Optional[int | str] = None   # Datastore document ID
    event_id: str

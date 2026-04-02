from pydantic import BaseModel


class OutboxEventResponseDTO(BaseModel):
    id: str
    data: str
    event_id: str
    event_type: str
    pending: bool


class PendingEventsResponseDTO(BaseModel):
    published: list[str]   # list of event_ids successfully published
    failed: list[str]      # list of event_ids that failed to publish
    total_processed: int

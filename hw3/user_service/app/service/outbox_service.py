from dtos.outbox_dto import PendingEventsResponseDTO
from repository.outbox_repository import OutboxRepository
from helpers.pubsub_helper import publish_message
from sqlalchemy.orm import Session

class OutboxService:
    def __init__(self, session: Session):
        self._repo = OutboxRepository(session)

    async def process_pending_events(self) -> PendingEventsResponseDTO:
        """
        Fetches all pending outbox events and publishes them to Pub/Sub.
        Marks each event as non-pending after successful publish.
        """
        pending = self._repo.get_pending()
        published = []
        failed = []

        for event in pending:
            try:
                await publish_message(
                    data=event.data,
                    event_type=event.event_type,
                    event_id=event.event_id,
                )
                self._repo.mark_as_published(event)
                published.append(event.event_id)
            except Exception as exc:
                # Log and continue — don't let one failure block others
                print(f"[OutboxService] Failed to publish event {event.event_id}: {exc}")
                failed.append(event.event_id)

        return PendingEventsResponseDTO(
            published=published,
            failed=failed,
            total_processed=len(pending),
        )

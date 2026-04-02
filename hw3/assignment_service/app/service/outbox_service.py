from app.dtos.outbox_dto import PendingEventsResponseDTO
from app.repository.outbox_repository import OutboxRepository
from app.helpers.pubsub_helper import publish_message


class OutboxService:
    def __init__(self):
        self._repo = OutboxRepository()

    async def process_pending_events(self) -> PendingEventsResponseDTO:
        """
        Fetches all pending outbox events and publishes them to Pub/Sub.
        Marks each event as non-pending after successful publish.
        """
        pending = await self._repo.get_pending()
        published = []
        failed = []

        for event in pending:
            try:
                await publish_message(
                    data=event.data,
                    event_type=event.event_type,
                    event_id=event.event_id,
                )
                await self._repo.mark_as_published(event.id)
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

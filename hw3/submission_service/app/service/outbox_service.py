from app.dtos.outbox_dto import PendingEventsResponseDTO
from app.repository.outbox_repo import OutboxRepository
from app.helpers.pubsub_helper import publish_message

class OutboxService:
    def __init__(self):
        self._repo = OutboxRepository()

    async def process_pending(self) -> PendingEventsResponseDTO:
        events = await self._repo.get_pending()
        pub, fail = [], []

        for e in events:
            try:
                await publish_message(data=e.data, event_type=e.event_type, event_id=e.event_id)
                await self._repo.mark_as_published(e.id)
                pub.append(e.event_id)
            except Exception as exc:
                print(f"[Outbox] Fail on {e.event_id}: {exc}")
                fail.append(e.event_id)

        return PendingEventsResponseDTO(published=pub, failed=fail, total_processed=len(events))
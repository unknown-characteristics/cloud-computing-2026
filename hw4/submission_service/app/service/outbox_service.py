from app.dtos.outbox_dto import PendingEventsResponseDTO
from app.repository.submission_repo import SubmissionRepository
from app.repository.rating_repo import RatingRepository
from app.helpers.pubsub_helper import publish_message


class OutboxService:
    def __init__(self):
        self._subm_repo = SubmissionRepository()
        self._rating_repo = RatingRepository()

    async def process_pending_events(self) -> PendingEventsResponseDTO:
        """
        Fetches all pending outbox events and publishes them to Pub/Sub.
        Marks each event as non-pending after successful publish.
        """
        subm_pending = self._subm_repo.get_pending_outbox_events()
        rating_pending = self._rating_repo.get_pending_outbox_events()
        published = []
        failed = []

        paired = [(self._subm_repo, subm_pending), (self._rating_repo, rating_pending)]
        for pair in paired:
            repo = pair[0]
            pending = pair[1]
            for event in pending:
                try:
                    await publish_message(
                        data=event.data,
                        event_type=event.event_type,
                        event_id=event.event_id,
                    )
                    repo.mark_outbox_published(event.id, event.partition_id)
                    published.append(event.event_id)
                except Exception as exc:
                    # Log and continue — don't let one failure block others
                    print(f"[OutboxService] Failed to publish event {event.event_id}: {exc}")
                    failed.append(event.event_id)

        return PendingEventsResponseDTO(
            published=published,
            failed=failed,
            total_processed=len(subm_pending)+len(rating_pending),
        )

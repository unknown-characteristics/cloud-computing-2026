from fastapi import APIRouter, status

from app.dtos.outbox_dto import PendingEventsResponseDTO
from app.service.outbox_service import OutboxService

router = APIRouter()
_service = OutboxService()


@router.post(
    "/pending-events",
    response_model=PendingEventsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Process and publish all pending outbox events to Pub/Sub",
)
async def pending_events() -> PendingEventsResponseDTO:
    return await _service.process_pending_events()

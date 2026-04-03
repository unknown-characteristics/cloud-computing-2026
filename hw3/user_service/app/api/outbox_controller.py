from fastapi import APIRouter, status, Depends

from dtos.outbox_dto import PendingEventsResponseDTO
from service.outbox_service import OutboxService
from core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/outbox", tags=["Outbox"])


@router.post(
    "/pending-events",
    response_model=PendingEventsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Process and publish all pending outbox events to Pub/Sub",
)
async def pending_events(db: Session = Depends(get_db)) -> PendingEventsResponseDTO:
    return await OutboxService(db).process_pending_events()

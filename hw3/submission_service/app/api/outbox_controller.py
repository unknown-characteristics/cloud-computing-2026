from fastapi import APIRouter
from app.dtos.outbox_dto import PendingEventsResponseDTO
from app.service.outbox_service import OutboxService

router = APIRouter()
_service = OutboxService()

@router.post("/pending-events", response_model=PendingEventsResponseDTO)
async def process_outbox():
    return await _service.process_pending()
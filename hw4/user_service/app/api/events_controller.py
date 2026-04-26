"""
Manual event-replay endpoint.

Production traffic comes through the Service Bus consumer in
`helpers.event_consumer`. This endpoint exists for ad-hoc testing and for
replaying a single event by hand. Body shape:
    {"event_id": "...", "event_type": "...", "data": "<inner-json-string>"}
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from service import user_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/receive",
    status_code=status.HTTP_200_OK,
    summary="Manually replay an event",
)
async def receive_event(envelope: dict, db: Session = Depends(get_db)):
    try:
        event_type = envelope["event_type"]
        event_id = envelope["event_id"]
        event_data = json.loads(envelope["data"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=400, detail=f"malformed envelope: {exc}"
        )

    if event_type == "assignment.created":
        user_service.change_user_assignment_count(
            event_data["creator_id"], db, event_id, increment=True
        )
    elif event_type == "assignment.deleted":
        user_service.change_user_assignment_count(
            event_data["creator_id"], db, event_id, increment=False
        )
    return {"status": "processed", "event_id": event_id}

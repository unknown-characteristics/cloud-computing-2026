from fastapi import APIRouter, status, Request, Depends
import base64, json
from service import user_service
from core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/events", tags=["Events"])

@router.post(
    "/receive",
    status_code=status.HTTP_200_OK,
    summary="Receive events from Pub/Sub",
)
async def receive_event(request: Request, db: Session = Depends(get_db)):
    event = await request.json()

    b64data = event["message"]["data"]

    event_json = json.loads(base64.b64decode(b64data).decode("utf-8"))
    print(event_json)
    event_data = json.loads(event_json["data"])

    if event_json["event_type"] == "assignment.created":
        user_service.change_user_assignment_count(event_data["creator_id"], db, event_json["event_id"], True)
    elif event_json["event_type"] == "assignment.deleted":
        user_service.change_user_assignment_count(event_data["creator_id"], db, event_json["event_id"], False)

from app.repository import other_event_repository
from app.service.assignment_service import AssignmentService
from fastapi import APIRouter, status, Request, HTTPException
import base64, json

router = APIRouter()

def _mark_event_as_handled(event_id: str):
    # create other event in order to mark it as handled
    repo = other_event_repository.OtherEventRepository()
    repo.create(event_id)

_service = AssignmentService()

@router.post(
    "/receive",
    status_code=status.HTTP_200_OK,
    summary="Receive events from Pub/Sub",
)
async def receive_event(request: Request):
    event = await request.json()

    b64data = event["message"]["data"]

    event_json = json.loads(base64.b64decode(b64data).decode("utf-8"))
    print(event_json)
    event_data = json.loads(event_json["data"])

    # if event_json["event_type"] == "assignment.deleted":
    #     assignment_service.delete_assignment(event_data["assignment_id"])
    #     _mark_event_as_handled(event_json["event_id"])
        
    if event_json["event_type"] == "user.deleted":
        # delete all assignments created by the deleted user
        user_assignments = _service.get_assignments_by_creator_id(event_data["user_id"])
        for assignment in user_assignments:
            try:
                await _service.delete_assignment(assignment.id)
            except HTTPException as e:
                if e.status_code == 404:
                    pass
                else:
                    raise e
        _mark_event_as_handled(event_json["event_id"])

from fastapi import APIRouter, status, Request, HTTPException
from app.repository import other_event_repo
import base64, json
from app.service.submission_service import SubmissionService

router = APIRouter()

def _mark_event_as_handled(event_id: str):
    # create other event in order to mark it as handled
    repo = other_event_repo.OtherEventRepository()
    repo.create(event_id)

_service = SubmissionService()

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

    
    if event_json["event_type"] == "assignment.deleted":
        assignment_id = event_data["assignment_id"]
        submissions = _service.get_all_by_assignment(assignment_id)
        for sub in submissions:
            try:
                await _service.delete(sub.id, -1)
            except HTTPException as e:
                if e.status_code == 404:
                    pass
                else:
                    raise e
        _mark_event_as_handled(event_json["event_id"])
        
    elif event_json["event_type"] == "user.deleted":
        # delete all submissions created by the deleted user
        user_submissions = _service.get_all_by_user(event_data["id"])
        for sub in user_submissions:
            try:
                await _service.delete(sub.id, -1)
            except HTTPException as e:
                if e.status_code == 404:
                    pass
                else:
                    raise e
        _mark_event_as_handled(event_json["event_id"])

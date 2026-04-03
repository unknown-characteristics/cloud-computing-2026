from fastapi import APIRouter, status, Request

router = APIRouter(prefix="/events", tags=["Events"])

@router.post(
    "/receive",
    status_code=status.HTTP_200_OK,
    summary="Receive events from Pub/Sub",
)
async def receive_event(request: Request):
    print(await request.json())

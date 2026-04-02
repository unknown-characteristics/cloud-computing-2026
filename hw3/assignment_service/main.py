from fastapi import FastAPI
from app.api.assignment_controller import router as assignment_router
from app.api.outbox_controller import router as outbox_router
from app.core.config import settings

app = FastAPI(
    title="Assignment Microservice",
    version="1.0.0",
    description="Microservice for managing assignments with Firestore and Pub/Sub outbox pattern",
)

app.include_router(assignment_router, prefix="/assignments", tags=["Assignments"])
app.include_router(outbox_router, prefix="/outbox", tags=["Outbox"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.SERVICE_NAME}

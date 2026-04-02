from fastapi import FastAPI
from app.api.submission_controller import router as sub_router
from app.api.rating_controller import router as rating_router
from app.api.outbox_controller import router as outbox_router

app = FastAPI(title="Submission Microservice")

app.include_router(sub_router, prefix="/submissions", tags=["Submissions"])
app.include_router(rating_router, prefix="/ratings", tags=["Ratings"])
app.include_router(outbox_router, prefix="/outbox", tags=["Outbox"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "submission-service"}
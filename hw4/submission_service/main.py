from app.api.submission_controller import router as sub_router
from app.api.rating_controller import router as rating_router
from app.api.outbox_controller import router as outbox_router
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.helpers.event_consumer import run_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    # Listen to its own events + global users topic
    tasks = [
        # asyncio.create_task(run_consumer("submissions-events", stop_event)),
        asyncio.create_task(run_consumer("assignments-events", stop_event)),
        asyncio.create_task(run_consumer("users-events", stop_event))
    ]
    try:
        yield
    finally:
        stop_event.set()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(
    title="Submission Microservice",
    lifespan=lifespan
)

app.include_router(sub_router, prefix="/submissions", tags=["Submissions"])
app.include_router(rating_router, prefix="/ratings", tags=["Ratings"])
app.include_router(outbox_router, prefix="/outbox", tags=["Outbox"])

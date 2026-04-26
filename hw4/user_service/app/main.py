import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.user_controller import router as user_router
from api.outbox_controller import router as outbox_router
from api.events_controller import router as events_router
from core.database import init_db
from helpers.event_consumer import run_consumer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("user_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    log.info("Initializing database schema")
    init_db()

    log.info("Starting Service Bus consumer")
    stop_event = asyncio.Event()
    consumer_task = asyncio.create_task(run_consumer(stop_event))

    try:
        yield
    finally:
        # --- Shutdown ---
        log.info("Stopping Service Bus consumer")
        stop_event.set()
        consumer_task.cancel()
        try:
            await consumer_task
        except (asyncio.CancelledError, Exception):
            pass


app = FastAPI(title="User Service", lifespan=lifespan)

app.include_router(user_router)
app.include_router(outbox_router)
app.include_router(events_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}

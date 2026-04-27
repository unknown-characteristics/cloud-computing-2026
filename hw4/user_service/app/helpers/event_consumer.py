"""
Background Service Bus consumer.

Reads messages from a topic subscription and dispatches them to handlers.
Started by FastAPI's lifespan (see main.py). Runs forever until cancelled.

Each message body is expected to be the JSON we publish in `pubsub_helper`:
    {"data": "<inner-json-string>", "event_type": "...", "event_id": "..."}
"""
import asyncio
import json
import logging
from typing import Awaitable, Callable

from azure.identity.aio import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.exceptions import ServiceBusError

from core.database import SessionLocal
from helpers.settings import settings
from service import user_service

log = logging.getLogger(__name__)

EventHandler = Callable[[dict], Awaitable[None]]


async def _handle_assignment_event(envelope: dict) -> None:
    event_type = envelope["event_type"]
    event_id = envelope["event_id"]
    event_data = json.loads(envelope["data"])

    db = SessionLocal()
    try:
        if event_type == "assignment.created":
            user_service.change_user_assignment_count(
                event_data["creator_id"], db, event_id, increment=True
            )
        elif event_type == "assignment.deleted":
            user_service.change_user_assignment_count(
                event_data["creator_id"], db, event_id, increment=False
            )
        else:
            log.info("Ignoring unhandled event_type=%s", event_type)
    finally:
        db.close()


HANDLERS: dict[str, EventHandler] = {
    "assignment.created": _handle_assignment_event,
    "assignment.deleted": _handle_assignment_event,
}


async def _dispatch(envelope: dict) -> None:
    try:
        handler = HANDLERS.get(envelope["event_type"])
    except KeyError:
        handler = None
        envelope["event_type"] = "unknown"

    if handler is None:
        log.info("No handler for event_type=%s; acking anyway", envelope["event_type"])
        return
    await handler(envelope)


async def run_consumer(topic_name: str, stop_event: asyncio.Event) -> None:
    """Long-running coroutine. Cancelled via `stop_event.set()`."""
    cred = DefaultAzureCredential()
    backoff = 1.0
    while not stop_event.is_set():
        try:
            async with ServiceBusClient(
                fully_qualified_namespace=settings.service_bus_namespace,
                credential=cred,
            ) as client:
                receiver = client.get_subscription_receiver(
                    topic_name=topic_name,
                    subscription_name=settings.service_bus_subscription,
                    max_wait_time=5,
                )
                async with receiver:
                    backoff = 1.0
                    while not stop_event.is_set():
                        msgs = await receiver.receive_messages(
                            max_message_count=10, max_wait_time=5
                        )
                        for msg in msgs:
                            try:
                                envelope = json.loads(b"".join(msg.body).decode("utf-8"))
                                await _dispatch(envelope)
                                await receiver.complete_message(msg)
                            except Exception:
                                log.exception("Handler failed; abandoning message")
                                await receiver.abandon_message(msg)
        except ServiceBusError:
            log.exception("Service Bus connection error; retrying in %.1fs", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
        except asyncio.CancelledError:
            break
    await cred.close()

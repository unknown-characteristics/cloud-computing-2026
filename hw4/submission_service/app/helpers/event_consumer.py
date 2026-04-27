import asyncio
import json
import logging
import httpx
from typing import Awaitable, Callable

from azure.identity.aio import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.exceptions import ServiceBusError
from app.repository.other_event_repo import OtherEventRepository
from app.service.submission_service import SubmissionService
from fastapi import HTTPException

from app.core.config import settings

log = logging.getLogger(__name__)

EventHandler = Callable[[dict], Awaitable[None]]

async def _handle_user_deleted(envelope: dict) -> None:
    event_data = json.loads(envelope["data"])
    event_id = envelope["event_id"]
    
    repo = OtherEventRepository()
    if repo.exists(event_id):
        return
        
    service = SubmissionService()
    user_submissions = service.get_all_by_user(event_data["id"])
    for sub in user_submissions:
        try:
            await service.delete(sub.id, -1)
        except HTTPException as e:
            if e.status_code == 404:
                pass
            else:
                raise e
    repo.create(event_id)

async def _handle_assignment_deleted(envelope: dict) -> None:
    event_data = json.loads(envelope["data"])
    event_id = envelope["event_id"]
    
    repo = OtherEventRepository()
    if repo.exists(event_id):
        return
        
    assignment_id = event_data["assignment_id"]
    service = SubmissionService()
    submissions = service.get_all_by_assignment(assignment_id)
    for sub in submissions:
        try:
            await service.delete(sub.id, -1)
        except HTTPException as e:
            if e.status_code == 404:
                pass
            else:
                raise e
    repo.create(event_id)

HANDLERS: dict[str, EventHandler] = {
    "user.deleted": _handle_user_deleted,
    "assignment.deleted": _handle_assignment_deleted,
}

async def _dispatch(envelope: dict) -> None:
    print("Dispatching event:", envelope)
    event_type = envelope.get("event_type")

    handler = HANDLERS.get(event_type)
    if handler is None:
        return
    await handler(envelope)

async def run_consumer(topic_name: str, stop_event: asyncio.Event) -> None:
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
                        msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
                        for msg in msgs:
                            try:
                                envelope = json.loads(b"".join(msg.body).decode("utf-8"))
                                await _dispatch(envelope)
                                await receiver.complete_message(msg)
                            except Exception:
                                log.exception("Handler failed; abandoning message")
                                await receiver.abandon_message(msg)
        except ServiceBusError:
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
        except asyncio.CancelledError:
            break
    await cred.close()
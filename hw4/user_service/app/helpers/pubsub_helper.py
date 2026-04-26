"""
Service Bus publisher. The function name `publish_message` and its signature are
kept identical to the old GCP Pub/Sub helper so that callers (outbox_service)
do not need to change.

Auth: DefaultAzureCredential picks the App Service Managed Identity (which
must have `Azure Service Bus Data Sender` on the namespace).
"""
import json
from functools import lru_cache
from typing import Optional

from azure.identity.aio import DefaultAzureCredential
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

from helpers.settings import settings


@lru_cache(maxsize=1)
def _credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def _client() -> ServiceBusClient:
    return ServiceBusClient(
        fully_qualified_namespace=settings.service_bus_namespace,
        credential=_credential(),
    )


async def publish_message(data: str | bytes, event_type: str, event_id: str) -> str:
    """Publish to the configured Service Bus topic. Returns the event_id
    (Service Bus does not return a message id at send time the way Pub/Sub does;
    we keep the same return type for API parity)."""
    if isinstance(data, bytes):
        body = data.decode("utf-8")
    else:
        body = data

    payload = json.dumps(
        {"data": body, "event_type": event_type, "event_id": event_id}
    )

    message = ServiceBusMessage(
        body=payload,
        content_type="application/json",
        message_id=event_id,
        subject=event_type,
        application_properties={
            "event_type": event_type,
            "event_id": event_id,
        },
    )

    async with _client() as client:
        async with client.get_topic_sender(topic_name=settings.service_bus_topic) as sender:
            await sender.send_messages(message)

    return event_id

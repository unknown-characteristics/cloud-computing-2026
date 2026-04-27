import json
from datetime import datetime
from azure.identity.aio import DefaultAzureCredential
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from app.core.config import settings

async def schedule_task(url_path: str, payload: dict, schedule_time: datetime) -> None:
    """
    Schedules an internal deadline check by scheduling a message in Service Bus 
    for future delivery. Replaces GCP Cloud Tasks.
    """
    cred = DefaultAzureCredential()
    
    body = json.dumps({
        "url_path": url_path,
        "payload": payload
    })

    message = ServiceBusMessage(
        body=body,
        content_type="application/json",
        application_properties={"event_type": "internal.deadline_reached"},
    )

    client = ServiceBusClient(
        fully_qualified_namespace=settings.service_bus_namespace,
        credential=cred,
    )

    async with client:
        async with client.get_topic_sender(topic_name=settings.service_bus_topic) as sender:
            await sender.schedule_messages(message, schedule_time_utc=schedule_time)
            
    await cred.close()
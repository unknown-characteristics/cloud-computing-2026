import json
from google.cloud import pubsub_v1
from app.core.config import settings

_publisher: pubsub_v1.PublisherClient | None = None


def get_publisher() -> pubsub_v1.PublisherClient:
    global _publisher
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
    return _publisher


def get_topic_path() -> str:
    publisher = get_publisher()
    return publisher.topic_path(settings.FIRESTORE_PROJECT_ID, settings.PUBSUB_TOPIC)


async def publish_message(data: str, event_type: str, event_id: str) -> str:
    """Publish a message to Pub/Sub. Returns the message ID."""
    publisher = get_publisher()
    topic_path = get_topic_path()

    payload = json.dumps({
        "data": data,
        "event_type": event_type,
        "event_id": event_id,
    }).encode("utf-8")

    future = publisher.publish(
        topic_path,
        payload,
        event_type=event_type,
        event_id=event_id,
    )
    return future.result()
